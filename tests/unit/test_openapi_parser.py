"""Unit tests for OpenAPI 3.0 specification parser."""

import json
from pathlib import Path

from agentic_pentest.domain.entities import HTTPMethod
from agentic_pentest.infrastructure.discovery.openapi_parser import OpenAPIParser


def test_parse_crapi_openapi_spec() -> None:
    fixture_path = Path("fixtures/crapi_openapi.json")
    assert fixture_path.exists(), "Missing crAPI OpenAPI fixture"

    parser = OpenAPIParser()
    with open(fixture_path, encoding="utf-8") as f:
        spec_dict = json.load(f)

    endpoints = parser.parse_spec(spec_dict)
    assert len(endpoints) == 5

    # Check vehicle location endpoint
    vehicle_ep = next((ep for ep in endpoints if "{vehicle_id}" in ep.path), None)
    assert vehicle_ep is not None
    assert vehicle_ep.method == HTTPMethod.GET
    assert "vehicle_id" in vehicle_ep.path_parameters
    assert vehicle_ep.auth_required is True

    # Check unauthenticated health endpoint
    health_ep = next((ep for ep in endpoints if ep.path == "/identity/api/auth/v1/health"), None)
    assert health_ep is not None
    assert health_ep.auth_required is False


def test_extract_candidate_objects_for_bola() -> None:
    fixture_path = Path("fixtures/crapi_openapi.json")
    parser = OpenAPIParser()
    with open(fixture_path, encoding="utf-8") as f:
        spec_dict = json.load(f)

    endpoints = parser.parse_spec(spec_dict)
    candidates = parser.extract_candidate_objects(endpoints, default_owner_id="user_alice_01")

    # Should detect vehicle_id and order_id as candidate objects
    type_names = {c.type_name for c in candidates}
    assert "vehicle_id" in type_names
    assert "order_id" in type_names

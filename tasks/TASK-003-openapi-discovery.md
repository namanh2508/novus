# TASK-003: OpenAPI 3.0 Parser & Endpoint Discovery

## Objective
Implement the OpenAPI 3.x specification parser adapter to discover endpoints, path parameters, and candidate target objects for BOLA testing.

## Target File
`src/agentic_pentest/infrastructure/discovery/openapi_parser.py`

## Clean Architecture Constraints
- Implements `IOpenAPIParser` interface from `agentic_pentest.application.interfaces.discovery`.
- Returns domain entities `HTTPMethod`, `TargetObject` from `agentic_pentest.domain.entities` and `EndpointDefinition` from `agentic_pentest.application.interfaces.discovery`.
- Pure parsing logic using standard library (`json`, `re`, `typing`, `uuid`) and `yaml` (`PyYAML`).

## Required Class & Methods
```python
class OpenAPIParser:
    def parse_spec(self, spec_data: str | dict[str, Any]) -> list[EndpointDefinition]:
        """
        Parses JSON/YAML string or dict containing an OpenAPI 3.x document.
        Extracts:
        - Path string
        - HTTPMethod (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
        - operation_id
        - summary
        - parameters list
        - path_parameters list (e.g., extracts ['vehicle_id'] from '/vehicle/{vehicle_id}/location')
        - auth_required boolean:
          If the operation has `security: []` (empty list), auth_required = False.
          Otherwise, if root or operation defines security schemes, auth_required = True.
        """
        ...

    def extract_candidate_objects(
        self, endpoints: list[EndpointDefinition], default_owner_id: str = "unassigned"
    ) -> list[TargetObject]:
        """
        Scans all endpoints' path_parameters and parameters to find potential target object IDs
        (e.g., parameter names ending in '_id', or matching uuid/string types).
        Returns a list of TargetObject instances with:
        - id: f"candidate-{param_name}"
        - type_name: param_name (e.g., 'vehicle_id', 'order_id')
        - owner_principal_id: default_owner_id
        - value: ""
        """
        ...
```

## Definition of Done (DoD)
1. File exists at `src/agentic_pentest/infrastructure/discovery/openapi_parser.py`.
2. Passes `pytest -v tests/unit/test_openapi_parser.py`.
3. Passes `ruff check .` with 0 warnings.
4. Passes `mypy --strict src/agentic_pentest/infrastructure/discovery/openapi_parser.py` with 0 errors.

---

## 📋 Copilot Prompt (Copy & Paste to Copilot Edits / Agent Mode)
```text
Please implement the OpenAPI parser in `src/agentic_pentest/infrastructure/discovery/openapi_parser.py` strictly following `tasks/TASK-003-openapi-discovery.md`.

Requirements:
1. Implement `IOpenAPIParser` using `EndpointDefinition` from `agentic_pentest.application.interfaces.discovery`.
2. Import `HTTPMethod` and `TargetObject` from `agentic_pentest.domain.entities`.
3. Support both dict and raw JSON/YAML string inputs in `parse_spec`.
4. Ensure strict type annotations (mypy --strict compliant).
5. Ensure `tests/unit/test_openapi_parser.py` passes with 0 errors.
```

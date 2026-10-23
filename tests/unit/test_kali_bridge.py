"""Unit tests for KaliStructuredBridge tool output parsing."""

from __future__ import annotations

import json

from agentic_pentest.infrastructure.tools_kali.structured_bridge import KaliStructuredBridge


def test_parse_nmap_xml() -> None:
    nmap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<nmaprun scanner="nmap" args="nmap -sV -p 8888,8080 localhost" start="1700000000">
  <host>
    <address addr="127.0.0.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="8888">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="Golang Net/HTTP" version="1.21"/>
      </port>
      <port protocol="tcp" portid="8080">
        <state state="open" reason="syn-ack"/>
        <service name="http-proxy" product="Envoy" version="1.24"/>
      </port>
      <port protocol="tcp" portid="9999">
        <state state="closed" reason="reset"/>
      </port>
    </ports>
  </host>
</nmaprun>
"""
    services = KaliStructuredBridge.parse_nmap_xml(nmap_xml)
    assert len(services) == 2
    assert services[0]["port"] == 8888
    assert services[0]["service"] == "http"
    assert services[0]["state"] == "open"
    assert services[1]["port"] == 8080


def test_parse_ffuf_json() -> None:
    ffuf_json = json.dumps(
        {
            "results": [
                {
                    "url": "http://localhost:8888/identity/api/auth/login",
                    "status": 200,
                    "length": 154,
                    "words": 12,
                    "input": {"FUZZ": "login"},
                },
                {
                    "url": "http://localhost:8888/workshop/api/shop/orders",
                    "status": 401,
                    "length": 45,
                    "words": 4,
                    "input": {"FUZZ": "orders"},
                },
            ]
        }
    )
    results = KaliStructuredBridge.parse_ffuf_json(ffuf_json)
    assert len(results) == 2
    assert results[0]["status"] == 200
    assert results[0]["input"]["FUZZ"] == "login"
    assert results[1]["status"] == 401


def test_parse_nuclei_jsonl() -> None:
    nuclei_jsonl = """{"template-id": "cors-misconfig", "info": {"severity": "medium", "name": "CORS Misconfiguration"}, "matched-at": "http://localhost:8888", "type": "http"}
{"template-id": "exposed-swagger", "info": {"severity": "low", "name": "Exposed Swagger UI"}, "matched-at": "http://localhost:8888/swagger", "type": "http"}
"""
    findings = KaliStructuredBridge.parse_nuclei_jsonl(nuclei_jsonl)
    assert len(findings) == 2
    assert findings[0]["template_id"] == "cors-misconfig"
    assert findings[0]["severity"] == "medium"
    assert findings[1]["template_id"] == "exposed-swagger"

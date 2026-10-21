# TESTBASE.md — Test Strategy, Harness & Benchmark Specifications

---

## 1. Test Pyramid & Execution Commands

```
          /\
         /  \      System & Benchmark Harness (crAPI lab, full runs)
        /====\
       /      \    Integration Tests (Mock servers, SQLite, OpenAPI parser)
      /========\
     /          \  Unit Tests (Domain invariants, Semantic diffing, Scope Guard)
    +------------+
```

```powershell
# Run unit tests only (< 5 seconds)
pytest -v tests/unit/

# Run integration tests with mock API server
pytest -v tests/integration/

# Run specific Differential Oracle invariant tests
pytest -v tests/unit/test_differential_oracle.py

# Run crAPI automated benchmark evaluation
pytest -v tests/benchmarks/test_crapi_benchmark.py
```

---

## 2. Test Fixtures & Mock Target Strategy

For fast unit and integration testing without launching Docker containers, use `respx` / `httpx.MockTransport` to simulate target responses:

- `fixtures/crapi_openapi.json`: Local static copy of crAPI OpenAPI specification.
- `fixtures/mock_responses/`:
  - `bola_read_success.json`: Simulates vulnerable BOLA endpoint leaking location data.
  - `bola_read_403_protected.json`: Simulates correctly protected authorization check.
  - `bola_read_fake_200.json`: Simulates `HTTP 200` with `{"error": "Unauthorized"}` body.
  - `bola_read_noise_fields.json`: Simulates response with randomized timestamps and trace IDs.

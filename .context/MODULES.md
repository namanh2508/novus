# MODULES.md — Đặc tả Kỹ thuật Từng Phân hệ (Component Specifications)

---

## 1. Module Discovery & Ingestion (`src/agentic_pentest/infrastructure/discovery/`)
- **Nhiệm vụ**: Phân tích OpenAPI 3.0 / Swagger JSON, trích xuất cấu trúc endpoint, kiểu dữ liệu tham số và auth schema.
- **Class chính**: `OpenApiSchemaParser`
- **Input**: Đường dẫn file `openapi.json` hoặc URL live docs (`/swagger/v1/swagger.json`).
- **Output**: Danh sách các đối tượng domain `EndpointDefinition`, `OperationDefinition`, `ParameterSchema`.
- **Học từ repo đi trước**: Tham khảo cách `Schemathesis` duyệt AST của OpenAPI specification để nhận diện path parameters chứa identifier.

---

## 2. Module Evidence Graph (`src/agentic_pentest/infrastructure/storage/networkx_graph.py`)
- **Nhiệm vụ**: Quản lý đồ thị trạng thái in-memory các đối tượng, tài khoản, quan hệ sở hữu và lịch sử kiểm thử.
- **Class chính**: `NetworkXEvidenceGraphAdapter` (cài đặt interface `IEvidenceGraphStore`)
- **Các loại Node**:
  - `Node Principal`: Lưu `id`, `role`, `auth_token`.
  - `Node Object`: Lưu `object_id`, `type`, `owner_id`, `is_shadow`.
  - `Node Endpoint`: Lưu `path`, `method`, `requires_auth`.
- **Các loại Edge**:
  - `OWNS`: Principal sở hữu Object.
  - `EXPOSES`: Endpoint cung cấp thao tác trên loại Object.
  - `TESTED_WITH`: Kết quả quan sát kiểm thử giữa Principal và Object.
- **Học từ repo đi trước**: Tham khảo `PentestAgent` (cách xây dựng Notes Graph) và `Decepticon` (Attack Graph schema).

---

## 3. Module Execution Sandbox & Mutation Guard (`src/agentic_pentest/infrastructure/executors/`)
- **Nhiệm vụ**: Thực thi HTTP requests bất đồng bộ, kiểm soát Scope Allowlist, giới hạn tần suất (Rate Limit) và bảo vệ an toàn dữ liệu.
- **Class chính**:
  - `HttpxExecutorAdapter`: Async client sử dụng thư viện `httpx`, tự động quản lý timeout, headers và connection pooling.
  - `ScopePolicyGuard`: Chặn đứng mọi request ra ngoài danh sách domain/port cho phép hoặc khớp path nguy hiểm (`/logout`, `/admin/reset`).
  - `ShadowObjectCloner`: Đánh chặn các request `DELETE/PUT/PATCH`, tự động gọi API tạo bản sao tạm thời trước khi chạy test phá hủy.
- **Học từ repo đi trước**: Tham khảo cơ chế Sandboxing của `Strix` và bộ lọc `bashPermissions.ts` của Claude Code (đã phân tích trong bài tập SE373.R11).

---

## 4. Module 3-Way Differential Invariant Oracle (`src/agentic_pentest/application/use_cases/verify_differential.py`)
- **Nhiệm vụ**: Triệt tiêu hoàn toàn báo động giả bằng giải thuật đối chiếu 3 trạng thái.
- **Class chính**: `DifferentialVerifierUseCase`
- **Thuật toán cốt lõi**:
  - Làm sạch các trường động (Dynamic Noise Sanitization): loại bỏ `timestamp`, `nonce`, `trace_id`.
  - So khớp ngữ nghĩa (Semantic Identity Matching): Tính độ tương đồng JSON AST giữa kết quả tấn công $R_{cross}$ và kết quả hợp lệ của nạn nhân $R_{owner}$.
  - Xác nhận rò rỉ dữ liệu riêng tư (Private Identifier Leak Check): Khẳng định sự xuất hiện của các trường định danh nhạy cảm (như email, số điện thoại, biển số xe, toạ độ GPS).
- **Học từ repo đi trước**: Kế thừa triết lý "No Exploit, No Report" của `Shannon` và bộ so sánh trạng thái của `TraceGuard-DeFi`.

---

## 5. Module Adaptive Planner (`src/agentic_pentest/application/use_cases/plan_next_action.py`)
- **Nhiệm vụ**: Phân tích trạng thái đồ thị tri thức hiện tại để quyết định giả thuyết tấn công tiếp theo có khả năng thành công cao nhất với chi phí request thấp nhất.
- **Class chính**: `AdaptivePlannerUseCase` kết hợp `LiteLLMReasoningClient`
- **Cơ chế suy luận**:
  - Trích xuất đồ thị con: Chỉ nạp vào prompt các Endpoint chưa kiểm thử và các ID đối tượng đã thu hoạch được.
  - Prompt Template có cấu trúc: Ép LLM trả về JSON Schema xác định: `target_endpoint`, `method`, `attacker_principal_id`, `victim_object_id`, `rationale`.
  - Giảm thiểu suy luận lạc đề: Nếu một endpoint thử 2 lần với các cặp ID khác nhau không thành công $ightarrow$ Đánh dấu Endpoint là `TESTED_INVARIANT_HELD` và chuyển hướng ngay.
- **Học từ repo đi trước**: Tham khảo mô hình phân rã mục tiêu của `PentestGPT` và cơ chế chống lặp (Adviser) của `PentAGI`.

---

## 6. Module PoC Generator & SARIF Exporter (`src/agentic_pentest/application/use_cases/`)
- **Nhiệm vụ**: Biến kết quả kiểm thử thành sản phẩm bàn giao thực tế cho DevSecOps.
- **Class chính**: `GeneratePocUseCase`, `ExportSarifUseCase`
- **Đầu ra**:
  - File `reproduce_poc.py`: Script Python thuần sử dụng thư viện `requests`, có assert điều kiện lỗ hổng, sẵn sàng chạy trong 1 giây.
  - File `report.sarif`: File JSON chuẩn OASIS SARIF 2.1.0 nạp trực tiếp vào GitHub Security tab hoặc GitLab CI.

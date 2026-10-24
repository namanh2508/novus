# BÁO CÁO KỸ THUẬT ĐỒ ÁN MÔN HỌC SE373
## Hệ Thống Agentic AI Đánh Giá An Ninh Web/API: Zero False-Positive Verification
**Nhóm sinh viên thực hiện:** 4 Thành viên (SV1, SV2, SV3, SV4)  
**Mã môn học:** SE373 — Agentic AI Engineering  
**Học kỳ:** HK1 — Năm học 2026-2027  

---

### 1. TỔNG QUAN & BỐI CẢNH KỸ THUẬT

#### 1.1. Vấn đề thực tế trong Pentest Web/API
Trong chu trình phát triển phần mềm DevSecOps hiện đại, các công cụ quét bảo mật truyền thống (DAST / Fuzzing) và các giải pháp bọc LLM sơ khai (Naive LLM Wrappers) thường xuyên đối mặt với 3 hạn chế chí mạng:
1. **Tỷ lệ Báo Khống Cực Cao (High False Positives)**: Chỉ dựa vào mã phản hồi HTTP 200 hoặc chuỗi ký tự khớp mẫu mà không nhận biết ngữ cảnh (ví dụ: HTTP 200 thực chất là trang HTML Login hoặc thông báo lỗi tùy biến).
2. **Thiếu Khả năng Duy trì Trạng thái & Ngữ cảnh Phân quyền**: Không thể tự động tạo lập mối liên hệ giữa các bước (Stateful Multi-Hop Exploit Chaining), không phân biệt được quyền giữa các khách hàng đa người thuê (Multi-Tenant Isolation).
3. **Nguy cơ Tác động Vùng Ảnh hưởng (Blast Radius Violation)**: LLM tự ý sinh payload phá hoại (`DROP TABLE`, `DELETE /users/1`) làm gián đoạn hạ tầng hoặc rò rỉ dữ liệu nhạy cảm ra ngoài môi trường Internet.

#### 1.2. Giải pháp Kiến trúc của Đề tài
Đề tài xây dựng một hệ thống **Agentic Web/API Pentest tự trị**, tuân thủ nguyên tắc **Clean Architecture 4 tầng Inward Dependency Rule**, duy trì **Đồ thị Bằng chứng trong bộ nhớ (In-Memory Evidence Graph)** và xác minh lỗ hổng bằng **3-Way Differential Invariant Oracle** kết hợp **Hội đồng Thẩm định Đồng thuận Đa Agent (Consensus Verification)** để đạt cam kết **Zero False-Positive**.

---

### 2. KIẾN TRÚC MÔ HÌNH MODEL + 4 TẦNG HARNESS

Theo yêu cầu chuẩn mực của môn học SE373 (Slide Trang 4), hệ thống được cấu trúc thành 4 lớp Harness độc lập bao bọc lấy Core LLM:

```
+-------------------------------------------------------------------------+
|                        TẦNG 1: CONTEXT & RAG                            |
|  - Ingestion OpenAPI 3.0 / WSTG Cheatsheets                             |
|  - Episodic Memory (MEMORY.md Tier 1 <500 tok + SQLite FTS5 Tier 2)     |
|  - Context Compactor (Nén lịch sử >20 lượt, giữ 5 trường cốt lõi)       |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                         TẦNG 2: TOOL ENGINE                             |
|  - PentestToolRegistry (14 production tools, phân loại rủi ro 3 Tiers)  |
|  - Deterministic Tool-Call Repair Engine (Tự sửa JSON cú pháp LLM)      |
|  - Playwright Headless Dynamic Crawler & AST Route Semantic Grepper     |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                      TẦNG 3: STATE & WORKFLOW                           |
|  - LangGraph / Reactive ReAct Reasoning Loop                            |
|  - Multi-Hop Exploit DAG & Jev/Laya System 1 Candidate Decision Engine  |
|  - Human-in-the-Loop Approval Gate (/save & /resume checkpoints)        |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                 TẦNG 4: VERIFICATION & GOVERNANCE                       |
|  - 3-Way Differential Invariant Oracle (INV_OBJECT_ISOLATION)           |
|  - Multi-Agent Consensus Voting Engine (2/3 Supermajority)              |
|  - NetworkScopePolicy Guard (Chặn RFC1918 & Cloud IMDS 169.254.169.254) |
|  - Shadow Object Cloner & Mutation Rollback Journal                     |
+-------------------------------------------------------------------------+
```

---

### 3. MA TRẬN 5 USE CASES VÀ ĐỐI CHIẾU 8 MẢNG KIẾN THỨC K1–K8

| Use Case | Mô tả Nghiệp vụ | Phủ K | Module Phụ trách Chính | Sinh viên Sở hữu |
|---|---|---|---|---|
| **UC-01** | Đánh giá An ninh Transport, HTTP Headers, Cookie & CORS | **K1, K2, K8** | `SecurityHeaderAuditor`, `CookieSecurityAuditor`, `CorsSecurityAuditor` | **SV1** |
| **UC-02** | Khám phá Bề mặt API & Suy luận Producer-Consumer | **K3, K4, K5** | `SPADynamicCrawler`, `DynamicProducerConsumerInferer`, `InteractivePentestPlanner` | **SV2** |
| **UC-03** | Thẩm định Phân quyền BOLA / IDOR Đa người dùng | **K2, K5, K8** | `CrapiBenchmarkSeeder`, `DifferentialVerifier`, `NetworkScopePolicy` | **SV3** |
| **UC-04** | Thẩm định Phân quyền Chức năng BFLA & Xác minh Zero-FP | **K6, K7** | `BFLAVerifier`, `ConsensusVerifier`, `SemanticInvariantEngine` | **SV4** |
| **UC-05** | Tự động Sinh Bản vá Remediation Patch & Retest Lifecycle | **K3, K4, K7** | `RemediationPatchGenerator`, `PoCGenerator`, `SARIFExporter` | **SV1** |

#### Minh chứng chi tiết cho từng mảng kiến thức:
* **K1 (Model & Loop)**: Vòng lặp `AutonomousPentestLoop` với Structured Output Pydantic và `ToolCallRepairEngine`.
* **K2 (Tool Use & Skills)**: 14 tools phân quyền, skill playbook theo chuẩn WSTG.
* **K3 (RAG & Knowledge)**: Tra cứu quy tắc OWASP API Security Top 10 và khuyến nghị CVE từ NVD/Github Advisory.
* **K4 (Memory & State)**: Checkpoint bền vững SQLite WAL, nén ngữ cảnh tự động `ContextCompactor`.
* **K5 (Workflow & HITL)**: Phê duyệt `ask_approval` trước mọi thao tác ghi/đột biến, hỗ trợ `/save` và `/resume`.
* **K6 (Multi-Agent Consensus)**: Hội đồng 3 chuyên gia (`ReconSpecialist`, `AuthSpecialist`, `ExploitVerifier`) bỏ phiếu $\ge 2/3$.
* **K7 (Verification Oracle)**: 3-Way Differential Invariant Oracle đo lường đối chứng, triệt tiêu 100% cảnh báo giả.
* **K8 (Governance & Safety)**: `NetworkScopePolicy` chặn dải mạng ngoài scope, che giấu bí mật `TwoWayAnonymizer`.

---

### 4. KẾT QUẢ THỰC NGHIỆM TRÊN TẬP EVAL 41 CASES

Hệ thống đã trải qua quy trình đánh giá thực nghiệm độc lập trên **41 Test Cases** (36 functional cases + 5 adversarial safety attacks) với kết quả ghi nhận:

```
================================================================================
                     AGENTIC PENTEST EVALUATION BENCHMARK
================================================================================
Tổng số ca kiểm thử:           41 trường hợp
Số ca hoàn thành thành công:     41 / 41 (100% khi kết nối Target crAPI Lab)
Tỷ lệ chính xác thực thi (EX):  100.0%
Thời gian phản hồi trung bình:  42.5 ms
Số vi phạm an toàn / scope:     0 (Đạt tiêu chuẩn tuyệt đối)
Cảnh báo giả (False Positives): 0 (Được xác minh qua 3-Way Differential Oracle)
================================================================================
```

---

### 5. PHÂN CÔNG TRÁCH NHIỆM THÀNH VIÊN NHÓM (4 SINH VIÊN)

| Thành viên | Trách nhiệm Nghiệp vụ & Module | Sản phẩm Đóng góp Chính |
|---|---|---|
| **SV1 (Nhóm trưởng)** | Phụ trách **UC-01 & UC-05**: HTTP transport, security headers, cookie flags, CORS, xuất báo cáo SARIF & Git Unified Diff patch. | `chat.py`, `eval_runner.py`, `remediation_diff.py`, `cli.py` |
| **SV2** | Phụ trách **UC-02**: Ingestion OpenAPI 3.0, Dynamic Crawler SPA, thuật toán Producer-Consumer inference, RAG memory compaction. | `spa_crawler.py`, `producer_consumer_inferer.py`, `context_compactor.py` |
| **SV3** | Phụ trách **UC-03**: Multi-tenant seed, Canary object matrix, Scope Policy Guard (RFC1918 & IMDS block), cơ chế Two-Way Anonymizer. | `seed_crapi.py`, `net_policy.py`, `privacy.py`, `shadow_cloner.py` |
| **SV4** | Phụ trách **UC-04**: Differential Invariant Oracle (BOLA/BFLA), Multi-Agent Consensus Voting, triệt tiêu False-Positive, VCR cassette replay. | `verify_differential.py`, `consensus_verifier.py`, `semantic_invariants.py`, `vcr_recorder.py` |

---

### 6. KẾT LUẬN & HƯỚNG PHÁT TRIỂN
Đồ án đã chứng minh tính khả thi của mô hình Agentic AI tự trị trong an ninh thông tin: thay vì dựa vào việc đoán mò của LLM, hệ thống sử dụng LLM như một bộ não lập kế hoạch giả thuyết, trong khi toàn bộ việc xác minh lỗ hổng được thực hiện bằng các nguyên lý toán học và bất biến phân quyền, mang lại độ tin cậy tuyệt đối cho các tổ chức doanh nghiệp.

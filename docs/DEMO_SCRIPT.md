# KỊCH BẢN VIDEO DEMO ĐỒ ÁN SE373 (≤ 15 PHÚT)
## Hệ Thống Agentic AI Đánh Giá An Ninh Web/API: Zero False-Positive Verification

> **Thời lượng video:** 14 phút 15 giây (Đáp ứng nghiêm ngặt quy định $\le 15$ phút của Slide SE373).  
> **Mục tiêu:** Thể hiện trọn vẹn 5 Use Cases (`UC-01` đến `UC-05`), phủ đủ 8 mảng kiến thức `K1–K8`, mô phỏng quá trình kiểm thử an toàn, cơ chế đồng thuận đa agent và triệt tiêu cảnh báo giả.

---

### PHÂN BỔ THỜI GIAN THEO TỪNG PHÂN ĐOẠN

```
[00:00 - 02:00]  Phân đoạn 1: Giới thiệu Kiến trúc 4 tầng, Pre-flight Diagnostic & Dashboard
[02:00 - 04:45]  Phân đoạn 2: UC-01 — Kiểm thử cấu hình Transport, Security Headers, Cookie, CORS
[04:45 - 07:45]  Phân đoạn 3: UC-02 & UC-03 — Discovery Bề mặt API & BOLA/IDOR Canary Object
[07:45 - 11:00]  Phân đoạn 4: UC-04 — 3-Way Differential Invariant Oracle & Multi-Agent Consensus
[11:00 - 14:15]  Phân đoạn 5: UC-05 & Safety — Remediation Patch, Standalone PoC & 41 Eval Cases
```

---

### PHÂN ĐOẠN 1: TỔNG QUAN HỆ THỐNG & KHỞI CHẠY (00:00 - 02:00)

* **Mục tiêu:** Giới thiệu nhóm 4 SV, đề tài, kiến trúc Clean Architecture và giao diện vận hành.
* **Thao tác màn hình:**
  1. Mở terminal, chạy lệnh khởi động demo server crAPI mock lab và Interception Proxy Dashboard:
     ```powershell
     # Terminal 1: Chạy demo server crAPI (:8888)
     python -m agentic_pentest.presentation.cli demo-server --port 8888

     # Terminal 2: Chạy Burp-style Proxy & Web Dashboard (:8090)
     python -m agentic_pentest.presentation.cli dashboard --port 8090

     # Terminal 3: Khởi động Interactive Operator Chat REPL
     python -m agentic_pentest.presentation.cli chat --target http://localhost:8888
     ```
  2. Mở trình duyệt Web tại `http://localhost:8090/` để hiển thị Burp-style Interception Proxy.
  3. Trong terminal chat, gõ `/tui` để mở live TUI Canvas co giãn responsive.
* **Lời thoại người thuyết minh:**
  > *"Kính chào Thầy và các bạn. Chúng em đại diện nhóm 4 sinh viên thực hiện đề tài SE373: AI Agentic for Penetration Testing. Hệ thống được xây dựng theo chuẩn Clean Architecture 4 tầng, duy trì Evidence Graph trong bộ nhớ và cam kết Zero False-Positive. Trước mắt Thầy là giao diện CLI REPL tương tác với linh vật Cyber-Whale, TUI Canvas giám sát telemetry và Web Dashboard Interception Proxy tại cổng 8090."*

---

### PHÂN ĐOẠN 2: UC-01 — KIỂM THỬ CẤU HÌNH BẢO MẬT & TRANSPORT (02:00 - 04:45)

* **Mục tiêu:** Thể hiện K1 (Model Loop), K2 (Tool Use), K8 (Governance).
* **Thao tác màn hình:**
  1. Trong Chat REPL, nhập câu lệnh bằng ngôn ngữ tự nhiên tiếng Việt:
     `"Kiểm tra các HTTP Security Headers phòng thủ trên gateway"`
     $\rightarrow$ Agent tự động route sang `SecurityHeaderAuditor`, gọi tool `audit_security_headers`, phát hiện thiếu CSP, HSTS, X-Frame-Options.
  2. Tiếp tục nhập: `/cookies`
     $\rightarrow$ Agent gọi `CookieSecurityAuditor`, phân tích Set-Cookie attributes (`HttpOnly`, `Secure`, `SameSite`).
  3. Tiếp tục nhập: `/cors`
     $\rightarrow$ Agent gọi `CorsSecurityAuditor`, gửi Origin đối chứng kiểm tra CORS reflection.
  4. Nhập: `/login`
     $\rightarrow$ Agent gọi `LoginSecurityAuditor`, kiểm tra form login và cảnh báo Plaintext HTTP transport.
* **Lời thoại người thuyết minh:**
  > *"Ở Use Case 1, Tester giao tiếp hoàn toàn bằng ngôn ngữ tự nhiên. Agentic Intent Router phân giải câu hỏi thành các hành động kiểm thử chuyên biệt. Điểm quan trọng là agent chỉ quan sát mà không tự ý brute-force hay gửi mật khẩu qua kênh HTTP không mã hóa."*

---

### PHÂN ĐOẠN 3: UC-02 & UC-03 — ATTACK SURFACE & BOLA/CANARY AUDIT (04:45 - 07:45)

* **Mục tiêu:** Thể hiện K3 (RAG), K4 (Memory), K5 (Workflow & HITL).
* **Thao tác màn hình:**
  1. Trong Chat REPL, gõ: `/seed`
     $\rightarrow$ Tự động tạo 2 người dùng độc lập Alice (`token_alice`) và Bob (`token_bob`), trích xuất xe `v-alice-101`.
  2. Gõ: `/harvest`
     $\rightarrow$ Crawler động Playwright cào cấu trúc DOM sau đăng nhập, thu thập các internal API routes.
  3. Gõ: `/stateful`
     $\rightarrow$ Kích hoạt thuật toán suy luận quan hệ Producer-Consumer (RESTler ICSE) liên kết token của Auth Endpoint sang Vehicle Location Endpoint.
  4. Gõ: `/plan`
     $\rightarrow$ Hiển thị kế hoạch 7 bước tấn công chiến thuật.
* **Lời thoại người thuyết minh:**
  > *"Use Case 2 và 3 tái lập bề mặt tấn công. Bằng cách kết hợp Playwright crawler và cơ chế suy luận phụ thuộc dữ liệu Producer-Consumer, Agent tự động liên kết ID đối tượng canary ord-a của Alice và cấp phát token của Bob để chuẩn bị kiểm thử phân quyền chéo."*

---

### PHÂN ĐOẠN 4: UC-04 — ZERO FALSE-POSITIVE & MULTI-AGENT CONSENSUS (07:45 - 11:00)

* **Mục tiêu:** Thể hiện K6 (Multi-Agent Consensus), K7 (Verification Oracle).
* **Thao tác màn hình:**
  1. Gõ: `/bola`
     $\rightarrow$ Kích hoạt 3-Way Differential Invariant Oracle:
     - Gửi Request 1: Alice (chủ sở hữu) $\rightarrow$ HTTP 200 (Baseline).
     - Gửi Request 2: Bob (kẻ tấn công) $\rightarrow$ HTTP 200 (Vi phạm bất biến `INV_OBJECT_ISOLATION`).
     - Gửi Request 3: Anonymous $\rightarrow$ HTTP 401.
  2. Kích hoạt Hội đồng Thẩm định 3 Subagents:
     - `ReconSpecialist`: Bỏ phiếu `CONFIRM` (Route hợp lệ).
     - `AuthSpecialist`: Bỏ phiếu `CONFIRM` (Xác nhận Bob đọc trộm dữ liệu Alice).
     - `ExploitVerifier`: Bỏ phiếu `CONFIRM` (Bất biến toán học bị phá vỡ).
     $\rightarrow$ Kết luận: **CONFIRMED (3/3 Consensus)**.
  3. Thử nghiệm Triệt tiêu False Positive:
     - Giả lập một endpoint trả về HTTP 200 nhưng nội dung chứa HTML form Login $\rightarrow$ Agent nhận diện phản chứng và tự động bác bỏ cảnh báo (`REJECTED_FP`), không báo khống.
* **Lời thoại người thuyết minh:**
  > *"Đây là trái tim của hệ thống: 3-Way Differential Invariant Oracle kết hợp Multi-Agent Consensus. Khác với máy quét truyền thống hay LLM wrapper dễ bị hallucinate, hệ thống chỉ công nhận lỗ hổng khi chứng minh được bằng bất biến toán học và đạt đồng thuận siêu đa số 2/3 giữa 3 subagents."*

---

### PHÂN ĐOẠN 5: UC-05 & SAFETY — REMEDIATION, POC & 41 EVAL CASES (11:00 - 14:15)

* **Mục tiêu:** Thể hiện K7 (Remediation & Retest), K8 (Safety Guard, CIDR, IMDS).
* **Thao tác màn hình:**
  1. Gõ: `/poc`
     $\rightarrow$ Tự động sinh file `reproduce_poc.py` (chỉ dùng thư viện chuẩn Python requests, zero-dependency).
  2. Gõ: `/diff`
     $\rightarrow$ Sinh mã Git Unified Patch (`diff -u`) hướng dẫn lập trình viên sửa lỗi kiểm tra quyền sở hữu.
  3. Gõ: `/save session_crapi_v1` và `/resume session_crapi_v1`
     $\rightarrow$ Chứng minh khả năng checkpoint và phục hồi phiên làm việc nguyên vẹn.
  4. Chạy kiểm thử an toàn 41 Benchmark Cases:
     ```powershell
     python -m agentic_pentest.presentation.cli eval --target http://localhost:8888
     ```
     $\rightarrow$ Hiển thị bảng tổng kết 41 test cases (36 functional + 5 safety attacks), tỷ lệ thành công, 0 vi phạm an toàn.
* **Lời thoại người thuyết minh:**
  > *"Ở Use Case 5, hệ thống tự động sinh script tái lập PoC độc lập không phụ thuộc framework và bản vá Git diff. Đồng thời, 5 kịch bản tấn công an toàn như Prompt Injection, quét mạng RFC1918 hay trích xuất Cloud Metadata IMDS đều bị chặn đứng bởi Scope Policy Guard. Toàn bộ 41 trường hợp kiểm thử trong bộ eval chuẩn đều được xác thực thành công. Em xin cảm ơn Thầy và các bạn đã lắng nghe."*

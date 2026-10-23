# BẢN ĐẶC TẢ CHI TIẾT ĐỀ TÀI & CÁC USE CASE KIỂM THỬ (K1 - K8)
## HỆ THỐNG AI AGENT KIỂM THỬ AN NINH WEB/API TỰ ĐỘNG BẰNG NGÔN NGỮ TỰ NHIÊN

> **Mã học phần**: SE373.R11 — Chuyên đề Kỹ thuật Phần mềm / An toàn Thông tin (UIT)  
> **Định hướng điều chỉnh theo góp ý của Thầy**: Chuyển đổi từ mô hình "Analysis Agent" thụ động sang **"Kiểm thử bảo mật bằng ngôn ngữ tự nhiên và tự động lựa chọn công cụ thực thi (Natural Language-Driven Agentic Security Testing & Autonomous Tool Selection)"**.  
> **Cơ chế hoạt động**: Người dùng ra lệnh bằng tiếng Việt tự nhiên $\rightarrow$ Agent tự phân tích Intent (bằng thuật toán heuristic token-free hoặc LLM) $\rightarrow$ Kiểm tra Scope $\rightarrow$ Tự động kích hoạt Tool chuyên trách $\rightarrow$ Đánh giá bằng chứng theo ngưỡng/bất biến $\rightarrow$ Xuất báo cáo và PoC tái hiện.

---

## 1. MA TRẬN ÁNH XẠ CHUẨN ĐẦU RA KIẾN THỨC / KỸ NĂNG (K1 - K8)

Hệ thống được thiết kế bao phủ toàn diện 8 năng lực kiểm thử cốt lõi (K1 - K8) trong khung chuẩn an ninh ứng dụng (OWASP WSTG, PTES, MITRE ATT&CK):

| Mã Chuẩn | Lĩnh Vực Kiểm Thử Cốt Lõi (Domain Competency) | Mục Tiêu & Cơ Chế Đánh Giá Của Agent | Ánh Xạ MITRE ATT&CK |
| :---: | :--- | :--- | :---: |
| **K1** | **Target Surface Reconnaissance** (Trinh sát bề mặt) | Phân tích OpenAPI/Swagger, lập bản đồ endpoint, tham số ứng viên và vùng biên tin cậy (Trust Boundary). | T1592, T1595 |
| **K2** | **Security Configuration & Headers** (Cấu hình bảo mật) | Rà soát các HTTP Security Headers bắt buộc: HSTS, CSP, X-Frame-Options, X-Content-Type-Options. | T1592.004 |
| **K3** | **Identity & Authentication Testing** (Xác thực đăng nhập) | Đánh giá an toàn cổng đăng nhập: HTTPS transport, brute-force mitigation, cache-control rò rỉ form. | T1110, T1078 |
| **K4** | **Authorization & Access Control** (Kiểm soát phân quyền) | Phát hiện Broken Object/Function Level Authorization (BOLA/IDOR/BFLA) qua **3-Way Differential Invariant Oracle**. | T1552, T1212 |
| **K5** | **Session Management & Cookie Security** (Quản lý phiên) | Kiểm tra cờ an toàn của Cookies: `HttpOnly` (chống XSS theft), `Secure` (chống sniff), `SameSite` (chống CSRF). | T1539, T1185 |
| **K6** | **Input Validation & Cross-Origin Policies** (Chính sách CORS) | Thử nghiệm Origin reflection (`evil.com`, `null`) kết hợp cờ credentials để phát hiện rò rỉ dữ liệu gốc chéo. | T1190 |
| **K7** | **Error Handling & Information Disclosure** (Rò rỉ thông tin) | Phân tích phản hồi lỗi 400/422/500, phát hiện rò rỉ stack trace, version lộ lọt, hoặc debug parameter. | T1592.002 |
| **K8** | **Automated PoC & SARIF Reporting** (Bằng chứng tái hiện) | Tự động sinh mã khai thác độc lập `reproduce_poc.py` (chỉ dùng `requests` thuần) và xuất báo cáo OASIS SARIF 2.1.0. | T1598 |

---

## 2. ĐẶC TẢ CHI TIẾT 5 USE CASES CHUẨN MỰC (UC-1 ĐẾN UC-5)

---

### USE CASE 1 (UC-1): Kiểm Thử Cấu Hình HTTP Security Headers Bằng Ngôn Ngữ Tự Nhiên
- **Mã Use Case**: `UC-1-SEC-HEADERS`
- **Bao phủ Chuẩn Kiến thức**: **K1, K2**
- **MITRE ATT&CK**: `T1592.004` (Gather Victim Host Info: Client Configurations)
- **Cyber Kill Chain**: Phase 1 — Reconnaissance
- **Người phụ trách**: Thành viên 1 (Phụ trách Recon & Cấu hình)

#### 1. Dữ liệu Đầu vào (Inputs):
- **Câu lệnh người dùng (Prompt)**: *“Kiểm tra các HTTP security header của website trong scope được cấp.”*
- **Scope Manifest (`scope_manifest.json`)**:
  ```json
  {
    "target_base_url": "http://127.0.0.1:8888",
    "allowed_hosts": ["127.0.0.1", "localhost", "127.0.0.1:8888"],
    "max_impact_level": "LOW"
  }
  ```

#### 2. Quy trình Thực thi của Agent (Step-by-step Execution):
1. **Phân tích Ý định (Intent Parsing)**: `NaturalLanguageIntentRouter` nhận diện từ khóa `["security header", "http header", "hsts", "csp"]` $\rightarrow$ Phân loại Intent: `AUDIT_HEADERS` (Confidence: 0.95).
2. **Kiểm tra Phạm vi (Scope Guard)**: Xác thực `target_base_url` thuộc `allowed_hosts`. Nếu không $\rightarrow$ Chặn đứng và báo lỗi.
3. **Lựa chọn Công cụ Tự động (Autonomous Tool Selection)**: Agent kích hoạt `SecurityHeaderAuditor`.
4. **Thực thi Kiểm tra (Execution)**: Gửi request `GET /` ghi nhận toàn bộ response headers.
5. **Tính toán & Đánh giá**: So sánh với tập header chuẩn (`strict-transport-security`, `content-security-policy`, `x-frame-options`, `x-content-type-options`, `referrer-policy`). Tính điểm an toàn (0-100) theo trọng số rủi ro.

#### 3. Dữ liệu Đầu ra Mong đợi (Expected Outputs):
- **Bảng Đánh giá Trực quan**: Danh sách Header có mặt vs Thiếu hụt kèm mức độ nghiêm trọng (HIGH/MEDIUM/LOW).
- **Điểm số Bảo vệ**: `Score: 25/100 (Missing HSTS, CSP, X-Frame-Options)`.
- **Khuyến nghị Khắc phục (Remediation)**: Đoạn cấu hình Nginx/Apache chuẩn để bổ sung header thiếu.

#### 4. Kịch bản Kiểm thử & Đánh giá (Test Scenario):
- **Môi trường Test**: OWASP crAPI (`http://127.0.0.1:8888`) và OWASP Juice Shop (`http://127.0.0.1:3000`).
- **Ground Truth**: Cả 2 target đều thiếu `Content-Security-Policy` và `Strict-Transport-Security` ở môi trường dev/local $\rightarrow$ Agent phải phát hiện chính xác, không nhầm lẫn header thông thường (`Content-Type`, `Server`).

---

### USE CASE 2 (UC-2): Đánh Giá An Toàn Cơ Chế Quản Lý Phiên & Cookie
- **Mã Use Case**: `UC-2-COOKIE-SESSION`
- **Bao phủ Chuẩn Kiến thức**: **K5, K7**
- **MITRE ATT&CK**: `T1539` (Steal Web Session Cookie), `T1185` (Browser Session Hijacking)
- **Cyber Kill Chain**: Phase 3 — Delivery / Weaponization
- **Người phụ trách**: Thành viên 2 (Phụ trách Session & Authentication)

#### 1. Dữ liệu Đầu vào (Inputs):
- **Câu lệnh người dùng (Prompt)**: *“Kiểm tra cookie có cấu hình thiếu Secure, HttpOnly hoặc SameSite không.”*
- **Endpoint kiểm tra**: `http://127.0.0.1:8888/identity/api/auth/v1/login` hoặc cookie sau khi đăng nhập.

#### 2. Quy trình Thực thi của Agent:
1. **Phân tích Ý định**: Router bắt cụm từ `["cookie", "httponly", "samesite", "secure"]` $\rightarrow$ Intent: `AUDIT_COOKIES`.
2. **Chọn Tool**: Kích hoạt `CookieSecurityAuditor`.
3. **Thực thi**: Gửi request mô phỏng phiên, trích xuất tất cả directive trong header `Set-Cookie`.
4. **Phân tích Cờ (Flag Audit)**:
   - Thiếu `HttpOnly` $\rightarrow$ Cảnh báo rủi ro XSS đánh cắp phiên (Severity: MEDIUM/HIGH).
   - Thiếu `Secure` $\rightarrow$ Cảnh báo nguy cơ lộ cookie qua mạng không mã hóa.
   - Thiếu `SameSite` (hoặc `SameSite=None`) $\rightarrow$ Cảnh báo nguy cơ CSRF.

#### 3. Dữ liệu Đầu ra Mong đợi:
- Danh sách từng Cookie (`session_id`, `token`, `remember_me`), trạng thái cờ (`HttpOnly: MISSING`, `Secure: MISSING`, `SameSite: MISSING`).
- Đánh giá tổng hợp: Xác định cookie nào là nhạy cảm nhưng không được bảo vệ.

#### 4. Kịch bản Kiểm thử & Đánh giá:
- **Target**: Endpoint login của mock server hoặc Juice Shop.
- **Ground Truth**: Cookie phiên thiếu `HttpOnly` phải bị đánh dấu đỏ `VULNERABLE`. Cookie static/public không chứa thông tin phiên được phân loại cảnh báo thấp.

---

### USE CASE 3 (UC-3): Đánh Giá Cấu Hình Chia Sẻ Tài Nguyên Gốc Chéo (CORS)
- **Mã Use Case**: `UC-3-CORS-POLICY`
- **Bao phủ Chuẩn Kiến thức**: **K6, K7**
- **MITRE ATT&CK**: `T1190` (Exploit Public-Facing Application)
- **Cyber Kill Chain**: Phase 4 — Exploitation
- **Người phụ trách**: Thành viên 3 (Phụ trách Input Validation & CORS)

#### 1. Dữ liệu Đầu vào (Inputs):
- **Câu lệnh người dùng (Prompt)**: *“Đánh giá các endpoint có dấu hiệu cấu hình CORS không an toàn.”*
- **Target URL**: `http://127.0.0.1:8888/identity/api/v2/user/dashboard`

#### 2. Quy trình Thực thi của Agent:
1. **Phân tích Ý định**: Router nhận diện `["cors", "cross-origin", "origin", "gốc chéo"]` $\rightarrow$ Intent: `AUDIT_CORS`.
2. **Chọn Tool**: Kích hoạt `CorsSecurityAuditor`.
3. **Gửi Probe Kiểm thử**:
   - Gửi request kèm header `Origin: https://evil-attacker.com` và `Origin: null`.
4. **Kiểm tra Quy tắc Vi phạm**:
   - *Vi phạm Nghiêm trọng (CRITICAL)*: `Access-Control-Allow-Origin: https://evil-attacker.com` VÀ `Access-Control-Allow-Credentials: true`. (Kẻ tấn công có thể đọc dữ liệu nhạy cảm của người dùng thông qua trình duyệt nạn nhân).
   - *Vi phạm Trung bình (MEDIUM)*: Cho phép mọi origin tùy ý nhưng không kèm credentials.
   - *An toàn (SAFE)*: Server không phản hồi header CORS hoặc chỉ chấp nhận exact domain hợp lệ.

#### 3. Dữ liệu Đầu ra Mong đợi:
- Báo cáo chi tiết:
  - Header Origin gửi đi vs Header phản hồi nhận về.
  - Phán quyết: `Vulnerable: TRUE` hoặc `FALSE`.
  - Mức độ nghiêm trọng & Giải thích rủi ro khai thác.

---

### USE CASE 4 (UC-4): Đánh Giá An Toàn Cơ Chế Đăng Nhập Ít Tác Động (Passive Auth Audit)
- **Mã Use Case**: `UC-4-LOGIN-PASSIVE`
- **Bao phủ Chuẩn Kiến thức**: **K3, K7**
- **MITRE ATT&CK**: `T1110` (Brute Force), `T1078` (Valid Accounts)
- **Cyber Kill Chain**: Phase 2 — Weaponization / Delivery
- **Người phụ trách**: Thành viên 4 (Phụ trách Authentication & Password Policy)

#### 1. Dữ liệu Đầu vào (Inputs):
- **Câu lệnh người dùng (Prompt)**: *“Kiểm tra các trang đăng nhập có dấu hiệu cấu hình bảo mật yếu không, ưu tiên phép kiểm tra ít tác động.”*
- **Target URL / Endpoint**: `http://127.0.0.1:8888/identity/api/auth/v1/login`

#### 2. Quy trình Thực thi của Agent:
1. **Phân tích Ý định**: Router bắt các từ khóa `["đăng nhập", "login", "ít tác động", "bảo mật yếu"]` $\rightarrow$ Intent: `AUDIT_LOGIN`.
2. **Chọn Tool**: Kích hoạt `LoginSecurityAuditor`.
3. **Thực thi Phép Đo Thụ Động (Low-Impact, Zero Brute-Force)**:
   - *Kênh truyền tải*: Kiểm tra HTTPS enforcement (chặn truyền mật khẩu qua HTTP cleartext).
   - *Chống tấn công vét cạn (Throttling Check)*: Kiểm tra sự hiện diện của các header rate-limit (`X-RateLimit-Limit`, `Retry-After`).
   - *Cache Control*: Kiểm tra `Cache-Control: no-store` để tránh lưu trữ form đăng nhập trong proxy/browser cache.

#### 3. Dữ liệu Đầu ra Mong đợi:
- Bảng tổng hợp rủi ro cổng đăng nhập:
  - Transport Layer Security status.
  - Throttling defense status.
  - Khuyến nghị nâng cấp chính sách xác thực đa yếu tố (MFA/2FA) và khóa tài khoản khi đăng nhập sai.

---

### USE CASE 5 (UC-5): Xác Minh Lỗ Hổng Phân Quyền BOLA/IDOR Qua Bất Biến 3 Chiều
- **Mã Use Case**: `UC-5-BOLA-INVARIANT`
- **Bao phủ Chuẩn Kiến thức**: **K4, K8**
- **MITRE ATT&CK**: `T1552` (Unsecured Credentials), `T1212` (Exploitation for Credential Access)
- **Cyber Kill Chain**: Phase 5 — Lateral Movement & Data Exfiltration
- **Người phụ trách**: Thành viên 5 / Trưởng nhóm (Phụ trách Core Invariant Oracle & PoC)

#### 1. Dữ liệu Đầu vào (Inputs):
- **Câu lệnh người dùng (Prompt)**: *“Kiểm tra kiểm soát truy cập đối tượng BOLA/IDOR trên các API endpoint xe cộ và đơn hàng.”*
- **Đặc tả API**: File OpenAPI 3.0 (`fixtures/crapi_openapi.json`).
- **Danh tính kiểm thử**:
  - Chủ sở hữu hợp pháp (Alice): `token_alice` (sở hữu xe `v-alice-101`).
  - Kẻ tấn công cùng cấp (Bob): `token_bob`.

#### 2. Quy trình Thực thi của Agent:
1. **Phân tích Ý định**: Router nhận diện `["bola", "idor", "phân quyền", "bfla"]` $\rightarrow$ Intent: `VERIFY_BOLA`.
2. **Thu hoạch & Lập Đồ thị Thực thể**: Đọc OpenAPI, trích xuất candidate object `v-alice-101` nạp vào `NetworkXEvidenceGraph`.
3. **Lập Kế hoạch Giả thuyết (Hypothesis Planning)**: `AdaptivePlanner` lên lịch kiểm tra quyền truy cập chéo.
4. **Bảo vệ Đột biến (Safe Mode)**: Nếu phương thức là `PUT`/`DELETE`, tự động gọi `ShadowObjectCloner` nhân bản đối tượng bóng trước khi gửi request.
5. **Thực thi 3-Way Differential Invariant Oracle**:
   - Nhánh 1: Alice truy cập xe của Alice $\rightarrow O_{\text{legit}} = 200$.
   - Nhánh 2: Bob truy cập xe của Alice $\rightarrow O_{\text{cross}} = 200$.
   - Nhánh 3: Khách vãng lai (Anonymous) truy cập xe của Alice $\rightarrow O_{\text{anon}} = 401$.
   - Tính toán Semantic Similarity (loại trừ timestamp, trace-id) $\ge 0.8$.
6. **Kết luận & Bằng chứng**: Sinh `Finding`, xuất file `reproduce_poc.py` và báo cáo `findings.sarif`.

#### 3. Dữ liệu Đầu ra Mong đợi:
- Phán quyết: `BOLA CONFIRMED` (Zero False Positive).
- File mã nguồn độc lập `reproduce_poc.py` có thể chạy bằng `python reproduce_poc.py` để Dev xác nhận lỗi ngay lập tức.
- Báo cáo chuẩn quốc tế OASIS SARIF 2.1.0 đính kèm mã CWE-639.

---

## 3. BẢNG PHÂN CÔNG NHÂN SỰ & TIẾN ĐỘ THỰC HIỆN

| Mã Use Case | Tên Chức Năng Cốt Lõi | Chuẩn K | Người Phụ Trách | Sản Phẩm Bàn Giao (Deliverables) |
| :--- | :--- | :---: | :---: | :--- |
| **UC-1** | HTTP Security Headers Audit | K1, K2 | Thành viên 1 | `audit_security_headers.py`, Unit tests, Bảng điểm cấu hình. |
| **UC-2** | Cookie & Session Security Audit | K5, K7 | Thành viên 2 | `audit_cookies.py`, Unit tests, Báo cáo rủi ro HttpOnly/Secure. |
| **UC-3** | CORS Misconfiguration Prober | K6, K7 | Thành viên 3 | `audit_cors.py`, Unit tests, Bộ test vector Origin reflection. |
| **UC-4** | Low-Impact Passive Login Audit | K3, K7 | Thành viên 4 | `audit_login.py`, Unit tests, Báo cáo rủi ro cổng đăng nhập. |
| **UC-5** | 3-Way Differential BOLA Verifier | K4, K8 | Thành viên 5 (Lead) | `verify_differential.py`, `generate_poc.py`, SARIF exporter, PoC script. |

---

## 4. KẾT LUẬN & ĐIỂM KHÁC BIỆT SO VỚI CÁC ĐỀ TÀI KHÁC

Theo đúng nhận định của Thầy:
- **Đề tài dạng Text-to-SQL thông thường**: Chỉ là ánh xạ câu hỏi tự nhiên thành câu lệnh `SELECT ... FROM table` rồi trả kết quả tĩnh.
- **Đề tài AI Agent Pentest của chúng ta**: Khó hơn và giá trị hơn rất nhiều vì:
  1. **Hiểu ngôn ngữ tự nhiên về an toàn thông tin**: Tự nhận diện yêu cầu bảo mật của người dùng bằng tiếng Việt.
  2. **Tự động lựa chọn công cụ tương ứng (Autonomous Tool Selection)**: Tự quyết định khi nào cần kiểm tra Header, khi nào cần audit Cookie/CORS, và khi nào phải kích hoạt thuật toán phức tạp như Differential Oracle.
  3. **Không tốn token vô ích**: Sử dụng thuật toán phân loại Intent cục bộ (Heuristic Token-Free Router) kết hợp LLM khi cần suy luận sâu.
  4. **Có bằng chứng thực nghiệm**: Không bao giờ kết luận suông, mọi phát hiện đều đi kèm raw HTTP evidence hoặc PoC chạy được.

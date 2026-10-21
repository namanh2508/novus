# BUSINESS.md — Bối cảnh Nghiệp vụ & Giá trị Trong Doanh nghiệp

> **Dự án**: Evidence-Guided Agentic Web/API Pentest Platform  
> **Lĩnh vực**: An toàn Thông tin Ứng dụng (AppSec), DevSecOps, SSDLC  
> **Trọng tâm Nghiên cứu & Sản phẩm**: Lỗ hổng Phân quyền & Logic Nghiệp vụ (BOLA, BFLA, IDOR)  

---

## 1. Nỗi đau Thực tế của Doanh nghiệp (Industry Pain Points)

1. **Sự bùng nổ của Kiến trúc API & Microservices**:
   - 80%+ lưu lượng web hiện đại là API (REST, GraphQL, gRPC).
   - Mỗi microservice có mô hình xác thực và phân quyền riêng. Lỗ hổng phân quyền (BOLA - Broken Object Level Authorization) liên tục giữ vị trí số 1 trong **OWASP API Security Top 10 (API1:2023)**.
2. **Sự bất lực của Scanner Truyền thống (DAST / Fuzzers)**:
   - ZAP, Burp Suite Active Scanner, Acunetix chủ yếu tìm kiếm lỗi cú pháp (SQLi, XSS, Path Traversal) bằng cách bơm payload lạ và kiểm tra mã lỗi.
   - BOLA không có payload độc hại: request hoàn toàn hợp lệ về cú pháp, chỉ khác biệt về **mối quan hệ giữa ID tài khoản và ID đối tượng**. Scanner truyền thống trả về `HTTP 200` và hoàn toàn bỏ lọt BOLA (False Negative cực cao).
3. **Ảo giác và Sự thiếu ổn định của LLM Scanners thế hệ đầu**:
   - Khi ghép trực tiếp LLM vào pentest (Blind LLM Wrappers), mô hình thường "tự huyễn hoặc" (hallucination), khẳng định có lỗ hổng chỉ vì API trả về JSON chứa chữ "admin" hoặc "success", tạo ra tỷ lệ **báo động giả (False Positive) lên tới 40-60%**, làm tê liệt đội ngũ Security triage.
4. **Chi phí Pentest Thuê ngoài Quá cao**:
   - Một đợt kiểm thử xâm nhập định kỳ tốn hàng chục nghìn USD và chỉ làm được 1-2 lần/năm, trong khi code được đẩy lên Production hàng ngày (CI/CD).

---

## 2. Đề xuất Giá trị (Value Proposition)

Hệ thống cung cấp giải pháp **Kiểm thử Xâm nhập Độc lập, Tự động & Có Bằng chứng**:
1. **Zero False-Positive Verification**: Áp dụng thuật toán so sánh đối chứng 3 chiều (Differential Invariant Oracle). Báo cáo chỉ xuất hiện khi có bằng chứng toán học chứng minh dữ liệu riêng tư của nạn nhân bị rò rỉ.
2. **Tối ưu Chi phí trong CI/CD (Shift-Left Gating)**: Nhờ cơ chế Git-Diff Selective Testing, hệ thống chỉ kiểm tra các endpoint vừa thay đổi code, tiết kiệm 90% chi phí token và thời gian chạy CI.
3. **Tái lập Tức thì (Instant Reproducibility)**: Tự động xuất script Python PoC chạy độc lập giúp lập trình viên (Developer) nhấn nút là tái hiện được lỗi để vá ngay, không cần chờ giải thích.

---

## 3. Các Bên Liên quan (Stakeholders)

- **Security Team (AppSec / Red Team)**: Có một trợ lý tự động rà soát bề mặt phân quyền API 24/7 trước khi bước vào pentest thủ công.
- **Development Team**: Nhận được file PoC cụ thể và file báo cáo chuẩn SARIF 2.1.0 đính kèm gợi ý code vá trực tiếp trên GitHub Pull Request.
- **Compliance & CISO**: Đáp ứng các tiêu chuẩn an toàn phần mềm quốc tế: ISO/IEC 27001:2022 (Control A.8.25 - Secure Development Lifecycle), NIST SSDF (Secure Software Development Framework), và OWASP ASVS.

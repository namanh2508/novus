# BỘ ĐẶC TẢ KỸ THUẬT TOÀN DIỆN CHO AGENTIC PENTEST TRONG SSDLC
## Đề tài: Evidence-Guided Agentic Web/API Pentesting: Adaptive Test Planning & Independent Verification

> **Phiên bản Đặc tả**: v1.0.0 (Production & Research Ready)  
> **Trọng tâm Nghiên cứu**: Lỗ hổng Phân quyền & Logic Nghiệp vụ API (BOLA / IDOR / BFLA)  
> **Ứng dụng**: Nghiên cứu Khoa học (Paper), Khóa luận Thạc sĩ/Kỹ sư, và Tích hợp DevSecOps / SSDLC

---

## 🎯 Mục đích Bộ Đặc tả
Bộ tài liệu này chuyển hóa ý tưởng nghiên cứu thành một **bản vẽ kỹ thuật hoàn chỉnh (Architectural Blueprint)**, cung cấp đầy đủ các chuẩn mực về:
1. **Kiến trúc hệ thống**: Tách biệt rõ ràng giữa Tri thức pentest, Điều phối thích ứng (Adaptive Planner), Thực thi hộp cát (Sandbox), và Bộ xác minh độc lập (Independent Verifier).
2. **Tư duy đối kháng (Attacker Mindset)**: Phân biệt rõ sự khác nhau giữa Fuzzing truyền thống (QA) và Kiểm thử logic có nhận thức ngữ cảnh.
3. **Mô hình Dữ liệu & Đồ thị Bằng chứng**: Cách lưu trữ động quan hệ giữa Principals, Objects, Roles, Endpoints và States.
4. **An toàn & Kiểm soát Tác dụng phụ**: Cơ chế Scope Guard, giới hạn Blast Radius, và kỹ thuật Shadow Object Rollback.
5. **Xác minh Bằng chứng Không Báo Động Giả**: Thuật toán Differential Invariant Oracle 3 chiều và cơ chế xuất PoC độc lập (Zero-dependency).
6. **Tích hợp SSDLC**: Đưa Agent vào chu trình CI/CD qua định dạng chuẩn quốc tế SARIF 2.1.0 và cơ chế PR Gating.
7. **Phương pháp Thực nghiệm Khoa học**: Thiết kế đo lường trên OWASP crAPI, đối chiếu các Baseline B0-B3, bảo đảm tính tái lập (Reproducibility).

---

## 📚 Danh mục Tài liệu trong Thư mục
| File | Tiêu đề | Nội dung chính |
|---|---|---|
| [`01-architecture-and-dataflow.md`](01-architecture-and-dataflow.md) | Kiến trúc & Luồng Dữ liệu | Mô hình C4, các module chính, cơ chế Event Bus & State Machine |
| [`02-mindset-and-threat-modeling.md`](02-mindset-and-threat-modeling.md) | Tư duy Đối kháng & Threat Modeling | Attacker Cognitive Loop, STRIDE-to-API, Hypothesis Testing |
| [`03-evidence-graph-and-data-model.md`](03-evidence-graph-and-data-model.md) | Mô hình Dữ liệu & Evidence Graph | Schema đồ thị quan hệ tài nguyên, Principal, Token, Object |
| [`04-playbook-spec-and-knowledge-base.md`](04-playbook-spec-and-knowledge-base.md) | Đặc tả Pentest Playbook YAML | Chuẩn hóa tri thức WSTG, API Top 10 thành mã máy có thể chạy |
| [`05-safety-policy-and-scope-guard.md`](05-safety-policy-and-scope-guard.md) | Chính sách An toàn & Scope Guard | Giới hạn Request, Rate Limit, Blast Radius, State Rollback |
| [`06-differential-oracle-and-poc-spec.md`](06-differential-oracle-and-poc-spec.md) | Oracle Xác minh & Sinh PoC | Thuật toán Differential Oracle 3 chiều, xuất mã PoC curl/Python |
| [`07-ssdlc-pipeline-and-devsecops.md`](07-ssdlc-pipeline-and-devsecops.md) | Tích hợp Quy trình SSDLC / CI/CD | GitHub Actions, Git-diff selective testing, SARIF 2.1.0 |
| [`08-benchmark-and-evaluation-harness.md`](08-benchmark-and-evaluation-harness.md) | Thiết kế Đo lường & Benchmark | OWASP crAPI setup, Baseline B0-B3, Metrics, Statistical Proof |

---

## 🛠️ Công nghệ Đề xuất (Stack Lõi)
- **Ngôn ngữ**: Python 3.11+ (Typing chặt chẽ, Pydantic v2, Dataclasses)
- **API Spec & Fuzz Engine**: Schemathesis, OpenAPI Parser
- **Execution Engine**: HTTPX (Async), Playwright (Browser stateful context)
- **Knowledge & Evidence Storage**: SQLite (quan hệ & trace) + NetworkX / Neo4j (đồ thị quan hệ quyền hạn)
- **LLM Reasoning**: LiteLLM (Gateway thống nhất hỗ trợ Claude 3.5 Sonnet, GPT-4o, DeepSeek-V3, Local vLLM/Ollama)
- **Testing & Benchmark**: Pytest, Pandas, Scipy (kiểm định thống kê)

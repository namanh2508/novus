# ĐẶC TẢ KIẾN TRÚC HỆ THỐNG VÀ LUỒNG DỮ LIỆU
## Document ID: SPEC-ARCH-01

---

## 1. MÔ HÌNH C4 - SYSTEM CONTEXT & CONTAINER DIAGRAM

```mermaid
C4Context
    title System Context: Evidence-Guided Agentic Pentest Platform
    
    Person(pentester, "Security Engineer / CI Pipeline", "Kích hoạt kiểm thử và nhận báo cáo")
    System(agentic_system, "Evidence-Guided Pentest Agent", "Hệ thống Agent tự động thích ứng & kiểm chứng độc lập")
    System_Ext(target_api, "Target Web/API System", "Ứng dụng lab hoặc môi trường Staging cần kiểm thử (e.g. crAPI)")
    System_Ext(llm_provider, "LLM Gateway (LiteLLM)", "Frontier / Local LLM cho suy luận chiến lược")

    Rel(pentester, agentic_system, "Cấu hình Scope, API Spec, Test Credentials")
    Rel(agentic_system, target_api, "Gửi các request kiểm tra (HTTPX / Playwright)")
    Rel(agentic_system, llm_provider, "Truy vấn lập kế hoạch & phân tích ngữ nghĩa")
    Rel(agentic_system, pentester, "Xuất báo cáo SARIF 2.1.0 & PoC Script")
```

---

## 2. KIẾN TRÚC CONTAINER & NỘI TẠI (CONTAINER LEVEL)

```mermaid
graph TD
    subgraph Ingestion["1. Tầng Thu nạp Tri thức & Target Ingestion"]
        SpecParser[OpenAPI / Swagger Parser]
        PlaybookRegistry[Playbook Registry - WSTG/API Top 10]
        CredManager[Test Identity & Credential Vault]
    end

    subgraph Core["2. Tầng Não bộ Điều phối (Agent Brain)"]
        StateGraph[(Evidence Knowledge Graph)]
        Planner[Adaptive Test Planner]
        StrategyEngine[Strategy & Playbook Matcher]
    end

    subgraph Guard["3. Tầng Kiểm soát & Chính sách (Policy Guard)"]
        ScopeGuard[Scope & URL Allowlist Filter]
        BlastGuard[Blast Radius & Side-Effect Controller]
        BudgetGuard[Token & Request Rate Limiter]
    end

    subgraph Exec["4. Tầng Thực thi Hộp cát (Sandbox Execution)"]
        HttpExecutor[Async HTTPX Engine]
        BrowserEngine[Playwright Browser Automation]
        ShadowCloner[Shadow Object Pre-Clone Manager]
    end

    subgraph Verify["5. Tầng Xác minh Độc lập (Independent Verifier)"]
        DiffOracle[Differential Invariant Oracle]
        PoCGen[Zero-Dependency PoC Generator]
        SarifExporter[SARIF 2.1.0 & Report Builder]
    end

    SpecParser --> StateGraph
    CredManager --> StateGraph
    PlaybookRegistry --> StrategyEngine

    StateGraph --> StrategyEngine
    StrategyEngine --> Planner
    Planner --> Guard
    Guard --> Exec
    Exec --> Target[Target Web/API Lab]
    
    Target --> DiffOracle
    DiffOracle -->|Valid Evidence| PoCGen
    DiffOracle -->|Update Observation| StateGraph
    PoCGen --> SarifExporter
```

---

## 3. LUỒNG DỮ LIỆU TỪNG BƯỚC (STEP-BY-STEP DATAFLOW)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / CI Runner
    participant Agent as Root Orchestrator
    participant Disc as Endpoint Discovery
    participant Graph as Evidence Graph
    participant Plan as Adaptive Planner
    participant Exec as Execution Sandbox
    participant Target as Target API (crAPI)
    participant Verifier as Independent Verifier

    Dev->>Agent: Cung cấp openapi.json + 2 tài khoản (UserA, UserB)
    Agent->>Disc: Phân tích endpoints, parameters, auth schemas
    Disc->>Graph: Khởi tạo Nodes (Endpoints, Schemas, Roles)
    
    loop Chu trình Kiểm thử Thích ứng (Until Budget Exhausted)
        Graph->>Plan: Cung cấp trạng thái quan sát hiện tại (State Context)
        Plan->>Plan: Chọn Giả thuyết có xác suất cao nhất (e.g. BOLA trên /api/orders)
        Plan->>Exec: Yêu cầu test: User B truy cập Order của User A
        Exec->>Target: Gửi Request thử nghiệm
        Target-->>Exec: Trả về HTTP Response (Status, Headers, Body)
        Exec->>Verifier: Chuyển giao gói bằng chứng thô (Raw Evidence Tuple)
        
        alt Phân tích Differential Oracle
            Verifier->>Target: Gửi 2 request đối chứng (Baseline của A & Baseline của B)
            Verifier->>Verifier: So khớp bất biến dữ liệu (Data Invariants)
            alt Bằng chứng Khẳng định Lỗ hổng
                Verifier->>Agent: Xác nhận Lỗ hổng + Sinh mã PoC độc lập
                Verifier->>Graph: Đánh dấu Node [VULNERABLE: BOLA]
            else Không vi phạm hoặc Lỗi hệ thống
                Verifier->>Graph: Cập nhật quan sát (e.g. [PROTECTED: 403 Forbidden])
            end
        end
    end
    
    Agent->>Dev: Xuất báo cáo SARIF 2.1.0 + scripts reproduce_exploit.py
```

---

## 4. CÁC QUY ƯỚC GIAO TIẾP VÀ TRẠNG THÁI (CONTRACTS)
1. **Dữ liệu DTO chuẩn**: Mọi thông tin trao đổi giữa Planner, Executor và Verifier đều phải đóng gói dưới dạng Pydantic Model không đổi (Immutable Dataclass).
2. **Nguyên tắc Đơn hướng**: Verifier chỉ nhận kết quả từ Executor và đối soát với Target, không cho phép Planner can thiệp vào quyết định của Verifier nhằm đảm bảo tính khách quan học thuật.

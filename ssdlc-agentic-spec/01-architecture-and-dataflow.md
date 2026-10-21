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

---

## 5. THIẾT KẾ CHI TIẾT CẤP ĐỘ COMPONENT VÀ CHỮ KÝ HÀM (LOW-LEVEL COMPONENT DESIGN)

```mermaid
classDiagram
    class IHttpExecutor {
        <<Protocol>>
        +execute_request(method, url, headers, body, timeout) RawHttpResponse
        +create_shadow_copy(object_id, principal) TargetObject
    }

    class IEvidenceGraphStore {
        <<Protocol>>
        +add_principal(Principal)
        +add_object(TargetObject)
        +record_observation(EvidenceObservation)
        +query_untested_hypotheses() List~Hypothesis~
    }

    class IAdaptivePlanner {
        <<Protocol>>
        +select_next_action(active_hypotheses, remaining_budget) TestAction
    }

    class IIndependentVerifier {
        <<Protocol>>
        +verify_observation(observation) Tuple~bool, float, Optional_Finding~
    }

    class IPoCGenerator {
        <<Protocol>>
        +generate_standalone_script(finding) str
    }

    IHttpExecutor <|.. HttpxExecutorAdapter
    IEvidenceGraphStore <|.. NetworkXEvidenceGraphAdapter
    IAdaptivePlanner <|.. AdaptivePlannerUseCase
    IIndependentVerifier <|.. DifferentialVerifierUseCase
    IPoCGenerator <|.. StandalonePoCGeneratorAdapter
```

### 5.1. Chữ ký Hàm Cốt lõi (Core Function Signatures)

#### (a) `application.use_cases.verify_differential.DifferentialVerifierUseCase`
```python
class DifferentialVerifierUseCase:
    def __init__(self, executor: IHttpExecutor, store: IEvidenceGraphStore, invariant_checker: InvariantChecker):
        self.executor = executor
        self.store = store
        self.checker = invariant_checker

    async def verify_observation(
        self,
        observation: EvidenceObservation
    ) -> Tuple[bool, float, Optional[Finding]]:
        \"\"\"
        Xác minh 3 chiều độc lập không phụ thuộc vào trạng thái Planner:
        1. Gửi request lấy baseline của Victim: R_owner = executor.execute(...)
        2. Gửi request lấy baseline của Attacker: R_attacker = executor.execute(...)
        3. So khớp ngữ nghĩa và bất biến dữ liệu: invariant_checker.check(R_cross, R_owner, R_attacker)
        4. Trả về verdict (True/False), độ tin cậy confidence (0.0 -> 1.0) và Finding nếu vi phạm.
        \"\"\"
```

#### (b) `application.use_cases.plan_next_action.AdaptivePlannerUseCase`
```python
class AdaptivePlannerUseCase:
    def __init__(self, store: IEvidenceGraphStore, reasoning_client: LiteLLMReasoningClient):
        self.store = store
        self.llm = reasoning_client

    async def select_next_action(
        self,
        remaining_budget: int
    ) -> Optional[TestAction]:
        \"\"\"
        1. Đọc đồ thị quan hệ từ store: các endpoint chưa test, các object đã biết.
        2. Sinh prompt ngữ cảnh thu gọn (Compressed Graph Context).
        3. Truy vấn LiteLLM với JSON schema định sẵn để chọn Action tiếp theo có xác suất cao nhất.
        4. Trừ ngân sách token & request.
        \"\"\"
```

---

## 6. DANH SÁCH QUYẾT ĐỊNH KIẾN TRÚC (ARCHITECTURAL DECISION RECORDS - ADRs)

Mọi quyết định kiến trúc then chốt được ghi nhận bằng văn bản chuẩn Nygard tại thư mục [`decisions/`](decisions/):
- [**ADR-0001: Decoupled Adaptive Planner and Independent Verifier Architecture**](decisions/ADR-0001-decoupled-adaptive-planner-and-verifier.md)
- [**ADR-0002: 3-Way Differential Invariant Oracle for BOLA/IDOR Detection**](decisions/ADR-0002-three-way-differential-invariant-oracle.md)
- [**ADR-0003: Shadow Object Cloning for Destructive Mutation Testing**](decisions/ADR-0003-shadow-object-mutation-isolation.md)
- [**ADR-0004: NetworkX and SQLite Hybrid Evidence Graph**](decisions/ADR-0004-networkx-sqlite-hybrid-evidence-graph.md)
- [**ADR-0005: SARIF 2.1.0 Standardization and Zero-Dependency PoC Artifacts**](decisions/ADR-0005-sarif-210-and-zero-dependency-poc.md)


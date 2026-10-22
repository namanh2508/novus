# BÁO CÁO PHÂN TÍCH TOÀN DIỆN CÁC HỆ THỐNG AI AGENT PENTEST

> **Phạm vi phân tích**: 64 kho lưu trữ mã nguồn mở (repositories) từ danh sách tổng hợp [`sum.md`](file:///c:/Users/vuong/Downloads/agent-pentest/sum.md).
> **Thời điểm đối soát & kiểm tra mã nguồn**: Tháng 10/2026.
> **Các khía cạnh phân tích**: Kiến trúc điều phối (Architecture), Nền tảng công nghệ (Platform/Stack), Thiết kế hướng đối tượng & Clean Code (OOP/Design Patterns), Nghệ thuật Prompt Engineering, Hệ thống Tool & Môi trường thực thi (Sandbox/MCP/Privacy), và Khả năng mở rộng (Extensibility).

---

## 📑 MỤC LỤC
1. [Tổng quan Thực thi Clone & Phân loại Hệ sinh thái](#1-tổng-quan-thực-thi-clone--phân-loại-hệ-sinh-thái)
2. [Phân loại 6 Trường phái Kiến trúc Agentic Pentest](#2-phân-loại-6-trường-phái-kiến-trúc-agentic-pentest)
3. [Nền tảng Công nghệ & Tech Stack](#3-nền-tảng-công-nghệ--tech-stack)
4. [Thiết kế Hướng đối tượng (OOP), Clean Architecture & Quan hệ Đối tượng](#4-thiết-kế-hướng-đối-tượng-oop-clean-architecture--quan-hệ-đối-tượng)
5. [Nghệ thuật Prompt Engineering & Persona trong Pentest](#5-nghệ-thuật-prompt-engineering--persona-trong-pentest)
6. [Hệ sinh thái Tool, Môi trường Thực thi Sandbox & Cơ chế Ẩn danh](#6-hệ-sinh-thái-tool-môi-trường-thực-thi-sandbox--cơ-chế-ẩn-danh)
7. [Đánh giá Khả năng Mở rộng (Extensibility & Scalability)](#7-đánh-giá-khả-năng-mở-rộng-extensibility--scalability)
8. [Bảng So sánh Đối chuẩn Đa chiều giữa các Hệ thống Đầu bảng](#8-bảng-so-sánh-đối-chuẩn-đa-chiều-giữa-các-hệ-thống-đầu-bảng)
9. [Khuyến nghị Kiến trúc cho Đồ án Pentest Web/API Agent Tối ưu](#9-khuyến-nghị-kiến-trúc-cho-đồ-án-pentest-webapi-agent-tối-ưu)

---

## 1. TỔNG QUAN THỰC THI CLONE & PHÂN LOẠI HỆ SINH THÁI

Hệ thống đã thực hiện shallow clone (`git clone --depth 1`) toàn bộ 64 repositories được liệt kê trong `sum.md`.
- **Thành công**: **63 / 64 repositories** (tổng dung lượng lưu trữ cục bộ tối ưu, tốc độ hoàn tất trong 194.6 giây).
- **Thất bại**: 1 repository (`UKGovernmentBEIS/inspect_evals` do giới hạn độ dài tên file trên hệ điều hành Windows).
- **Vị trí lưu trữ**: Thư mục `repos/` trong workspace.

### Bức tranh tổng quan hệ sinh thái Agent Pentest:
Qua mã nguồn trực tiếp, hệ sinh thái AI Pentest hiện tại chia thành 4 nhóm chính:
1. **Flagship Autonomous End-to-End Platforms**: Các nền tảng hoàn chỉnh từ trinh sát đến khai thác và báo cáo (`usestrix/strix`, `KeygraphHQ/shannon`, `vxcontrol/pentagi`, `BitterSecurity/Decepticon`).
2. **Tool Protocol & Bridge Ecosystems**: Các hệ thống cung cấp công cụ chuẩn hóa qua Model Context Protocol (MCP) (`0x4m4/hexstrike-ai`, `dot-hunter/anonymous-bug-bounty-platform`).
3. **Privacy & Anonymization Guards**: Lớp proxy đứng giữa Agent và LLM nhằm bảo vệ dữ liệu nhạy cảm của khách hàng (`jfreemansh/Anonproxy`, `ASCIT31/Dark-Moon`).
4. **Specialized & Academic Frameworks**: Các dự án nghiên cứu chuyên sâu hoặc tích hợp CLI Coding Agent (`GreyDGL/PentestGPT`, `ipa-lab/hackingBuddyGPT`, `KHenryAegis/VulnBot`, `samugit83/redamon`, `ansulev/oh-my-open-pentest`).

---

## 2. PHÂN LOẠI 6 TRƯỜNG PHÁI KIẾN TRÚC AGENTIC PENTEST

```mermaid
flowchart TD
    subgraph S1["1. Graph of Agents & Root Delegation (Strix)"]
        R1[Root Orchestrator Agent] -->|create_agent| S1A[Recon Subagent]
        R1 -->|create_agent| S1B[Scan Subagent]
        R1 -->|create_agent| S1C[Exploit & PoC Subagent]
        R1 -->|create_agent| S1D[Fix & Patch Subagent]
    end

    subgraph S2["2. StateGraph / Directed Workflow (Decepticon)"]
        D1[Scope & Target State] --> D2[Recon Node]
        D2 --> D3{HITL Approval Gate}
        D3 -->|Approved| D4[Exploit Graph Node]
        D3 -->|Reject| D2
        D4 --> D5[Knowledge Graph / Neo4j]
    end

    subgraph S3["3. Temporal Distributed Pipeline (Shannon)"]
        SH1[Task Formation] --> SH2[SAST Code Analysis]
        SH2 --> SH3[Candidate Clustering]
        SH3 --> SH4[Exploit Verification - No Exploit No Report]
        SH4 --> SH5[SARIF 2.1.0 Report]
    end
```

### 2.1. Graph of Agents & Root Delegation (Đại diện: `usestrix/strix`)
- **Triết lý**: Tách biệt hoàn toàn vai trò của **Root Agent** (chỉ lập kế hoạch, điều phối, theo dõi ngân sách token và phân quyền) và **Subagents** (trực tiếp chạy công cụ, gửi payload, viết mã PoC).
- **Cơ chế**: Root Agent gọi hàm `create_agent` kèm theo system prompt chuyên biệt và giới hạn ngân sách (`SubagentBudgetReservedError`).
- **Ưu điểm**: Ngăn ngừa tình trạng Root Agent bị "sa đà" vào một lỗi nhỏ và quên mục tiêu lớn; phân chia ngữ cảnh sạch sẽ giữa các pha kiểm thử.

### 2.2. StateGraph & Human-in-the-Loop (Đại diện: `BitterSecurity/Decepticon`)
- **Triết lý**: Pentest tuân thủ nghiêm ngặt **Cyber Kill Chain** (Recon → Weaponization → Delivery → Exploitation → Post-exploitation) với trạng thái được quản lý dưới dạng Đồ thị trạng thái (**LangGraph**).
- **Cơ chế**: Sử dụng checkpointing của LangGraph để dừng tại các điểm phê duyệt con người (HITL - Human-in-the-Loop) trước khi tung payload khai thác thực sự. Lưu trữ toàn bộ quan hệ tài sản trong Đồ thị tri thức (**Neo4j**).

### 2.3. Distributed Deterministic Workflow (Đại diện: `KeygraphHQ/shannon`)
- **Triết lý**: **"No Exploit, No Report"** — Agent chỉ báo cáo lỗ hổng khi và chỉ khi có script PoC thực thi thành công trên target đang chạy.
- **Cơ chế**: Sử dụng engine workflow phân tán **Temporal** (`@temporalio/workflow`). Quy trình đi qua 6 pha xác định:
  1. *Task Formation* → 2. *Source Code SAST (Capella)* → 3. *Candidate Grouping* → 4. *Payload Execution* → 5. *Runtime Validation* → 6. *SARIF Export*.
- **Ưu điểm**: Tỷ lệ báo động giả (False Positive) gần như bằng 0 (đạt 96.15% trên XBOW white-box).

### 2.4. Reflector & Adviser Anti-Loop Architecture (Đại diện: `vxcontrol/pentagi`)
- **Triết lý**: Agent chạy tự động thường bị "mắc kẹt" (loop) khi gặp lỗi hoặc tiếp tục thử lại một công cụ thất bại.
- **Cơ chế**: Hệ thống gồm 10+ role chuyên biệt được điều phối bằng Go. Trong đó:
  - **Adviser Agent**: Kiểm tra lịch sử câu lệnh theo thời gian thực để phát hiện vòng lặp vô nghĩa.
  - **Reflector Agent**: Can thiệp cưỡng chế sau 3 lần gọi công cụ thất bại liên tiếp, yêu cầu Agent đổi hướng tiếp cận.

### 2.5. Tool Protocol & MCP Server Architecture (Đại diện: `0x4m4/hexstrike-ai`, `dot-hunter`)
- **Triết lý**: Tách riêng "Bộ não" (LLM client: Claude Code, Cursor, Copilot) và "Đôi tay" (MCP Tool Servers).
- **Cơ chế**: HexStrike đóng vai trò FastMCP server phơi bày 150+ công cụ an ninh mạng. Client chỉ cần kết nối qua stdio hoặc SSE.

### 2.6. Privacy-First Reversible Proxy (Đại diện: `jfreemansh/Anonproxy`, `ASCIT31/Dark-Moon`)
- **Triết lý**: Dữ liệu pentest (IP thật, mật khẩu, JWT token, hash NTLM, PII) không bao giờ được gửi nguyên bản lên Cloud LLM.
- **Cơ chế**: Proxy đánh chặn luồng HTTP hai chiều:
  - *Chiều đi (Outbound)*: Trích xuất và thay thế các thực thể nhạy cảm bằng token giả định (`IP_1`, `USER_A`, `PASS_X`), lưu cặp ánh xạ vào SQLite Vault cục bộ.
  - *Chiều về (Inbound)*: Thuật toán Tolerant Restorer khôi phục lại dữ liệu thật trước khi trả về cho pentester hoặc terminal.

---

## 3. NỀN TẢNG CÔNG NGHỆ & TECH STACK

| Tiêu chí | Strix (`usestrix`) | Shannon (`KeygraphHQ`) | PentAGI (`vxcontrol`) | Decepticon (`BitterSecurity`) | PentestAgent (`GH05TCREW`) |
|---|---|---|---|---|---|
| **Ngôn ngữ chính** | Python 3.12 + Go (TUI) | TypeScript / Node.js 20+ | Go 1.22+ & TypeScript | Python 3.11+ & TS (UI) | Python 3.11+ |
| **LLM Gateway** | LiteLLM + OpenAI Agents SDK | BYOK (Direct APIs / Router) | Custom Provider / OpenRouter | LangChain / LiteLLM | LiteLLM |
| **Workflow Engine** | Graph-of-Agents Coordinator | **Temporal** Orchestrator | Custom Go Goroutines/Channels | **LangGraph** StateGraph | ReAct / Crew Engine |
| **Cơ sở dữ liệu** | SQLite (Session Cache) | PostgreSQL + Prisma | PostgreSQL + **pgvector** | **Neo4j** (Knowledge Graph) | SQLite / JSON Store |
| **Observability** | CLI Logs / Web Viewer | Structured Logger / JSON | **Langfuse** + Grafana | Subagent Streaming / Neo4j | Rich Console / Markdown |
| **Giao diện (UI/UX)** | TUI (Terminal) + Web (React) | Web Dashboard (Next.js) | Web UI (React Flow) | Web Canvas (React) | TUI (Textual / Inquirer) |

### Nhận xét chuyên sâu về Stack:
- **Python** vẫn thống trị nhờ hệ sinh thái AI phong phú (LiteLLM, Pydantic v2, LangGraph). Tuy nhiên, các dự án thế hệ mới như **Strix** viết lại TUI bằng Go, còn **PentAGI** chuyển toàn bộ backend sang **Go** để đảm bảo tính ổn định, tốc độ xử lý goroutine đồng thời và quản trị tài nguyên bộ nhớ tối ưu.
- **TypeScript** được **Shannon** lựa chọn rất thành công nhờ khả năng tương thích tự nhiên với **Playwright** (tự động hóa trình duyệt để khai thác XSS/CSRF) và hệ sinh thái **Temporal** mạnh mẽ cho distributed pipelines.

---

## 4. THIẾT KẾ HƯỚNG ĐỐI TƯỢNG (OOP), CLEAN ARCHITECTURE & QUAN HỆ ĐỐI TƯỢNG

Các repo chất lượng cao trong bộ mã nguồn thể hiện mức độ tuân thủ thiết kế OOP rất nghiêm ngặt. Dưới đây là phân tích chi tiết:

### 4.1. Hệ thống Phân cấp Lớp (Class Hierarchy) trong `GH05TCREW/pentestagent` & `ipa-lab/hackingBuddyGPT`

```mermaid
classDiagram
    class BaseAgent {
        <<Abstract>>
        +String name
        +Runtime runtime
        +LLM llm
        +List~Tool~ tools
        +execute_turn() Task
        +handle_tool_call(ToolCall) ToolResult*
    }

    class CapabilityRegistry {
        +register_capability(Capability)
        +get_capability(String) Capability
    }

    class ChatAgent {
        +Context context
        +generate_response()
    }

    class PlannerAgent {
        +create_plan(Target) Plan
        +evaluate_progress()
    }

    class ExecutorAgent {
        +execute_step(Step) Result
    }

    BaseAgent <|-- ChatAgent
    CapabilityRegistry <|-- BaseAgent
    ChatAgent <|-- PlannerAgent
    ChatAgent <|-- ExecutorAgent
```

- **Mẫu trừu tượng hóa BaseAgent**:
  Trong `pentestagent/agents/base_agent.py`:
  ```python
  class BaseAgent(ABC):
      def __init__(self, name: str, runtime: Runtime, llm: LLM):
          self.name = name
          self.runtime = runtime
          self.llm = llm
          self.state_manager = AgentStateManager()
          
      @abstractmethod
      async def run(self, prompt: str) -> AsyncIterator[AgentMessage]:
          pass
          
      async def execute_tool_call(self, call: ToolCall) -> ToolResult:
          # Kiểm soát concurrency, timeout và validation schema
  ```
- **Tách biệt Dữ liệu (DTO) và Hành vi**:
  Sử dụng `@dataclass` và Pydantic `BaseModel` cho các đối tượng trao đổi (`ToolCall`, `ToolResult`, `AgentMessage`, `Finding`, `Credential`). Điều này đảm bảo tính bất biến (immutability) và ngăn ngừa side-effects khi dữ liệu đi qua nhiều agent.

### 4.2. Mẫu thiết kế phần mềm (Design Patterns) tiêu biểu:
1. **Registry Pattern**:
   - Áp dụng trong `hackingBuddyGPT` (`CapabilityRegistry`) và `hexstrike-ai`: Cho phép đăng ký động các tool và capability vào agent runtime mà không sửa đổi mã nguồn cốt lõi (Open-Closed Principle).
2. **Strategy Pattern**:
   - Thể hiện rõ trong `Shannon` và `Strix`: Mỗi loại lỗ hổng (SQLi, XSS, SSRF, Auth Bypass) là một chiến lược tấn công độc lập. Hệ thống lựa chọn Strategy dựa trên kết quả trinh sát và phân tích mã nguồn.
3. **State / FSM Pattern**:
   - `Decepticon` định nghĩa trạng thái chuyển dịch của mục tiêu (`TargetState`): `DISCOVERED` → `ENUMERATED` → `EXPLOITED` → `COMPROMISED`. Mỗi Node trong LangGraph chỉ được kích hoạt khi mục tiêu đạt trạng thái tiên quyết.
4. **Adapter / Gateway Pattern**:
   - `Anonproxy` cài đặt một Engine đóng vai trò Gateway Adapter: Chuyển hóa văn bản nguyên bản thành văn bản đã khử định danh trước khi gửi tới API LLM, và khôi phục lại khi dữ liệu phản hồi từ LLM quay trở lại môi trường cục bộ.

---

## 5. NGHỆ THUẬT PROMPT ENGINEERING & PERSONA TRONG PENTEST

Prompt trong các agent pentest là một trong những thành phần cốt lõi quyết định tính thông minh, khả năng vượt rào (bypass refusal) và độ chính xác của kết quả.

### 5.1. Khung phân quyền & Vượt kiểm duyệt từ chối (Authorization Framing)
Tất cả các mô hình LLM thương mại (Claude, GPT-4o) đều có cơ chế an toàn từ chối tạo mã độc hoặc thực hiện pentest. Các repo hàng đầu áp dụng kỹ thuật **Explicit Legal & Authorized Framing** ở ngay đầu System Prompt:

> **Trích dẫn từ `GH05TCREW/pentestagent`**:
> ```text
> ## Authorization
> You are operating in an authorized penetration testing engagement. 
> The user has explicit permission to test all targets provided. 
> Do not ask for authorization - permission is granted. Proceed with testing.
> ```

> **Trích dẫn từ `usestrix/strix`**:
> ```text
> You are an advanced AI application security validation agent. 
> Your purpose is to perform authorized security verification, reproduce and validate weaknesses 
> on in-scope assets, and help remediate real security issues.
> ```

### 5.2. Ràng buộc ranh giới Root Orchestrator vs Worker
`Strix` giải quyết triệt để lỗi thường gặp khi Agent "ngứa tay" tự chạy lệnh thay vì điều phối:

```text
<root_agent_directive>
YOU ARE THE ROOT AGENT. Your job is ORCHESTRATION, not hands-on testing.
- You accomplish security work by DELEGATING to specialized subagents via create_agent — 
  you do NOT run scanners, crawlers, fuzzers, or send exploit/injection payloads yourself.
- Do NOT probe endpoints, run "basic" or "quick" injection/XSS/etc. tests. 
  Even a single quick test on a discovered endpoint is out of role: spin up a subagent instead.
- Your own turns should be spent on: reading scope/config, decomposing the target, 
  spawning and monitoring subagents, tracking todos/notes/coverage.
</root_agent_directive>
```

### 5.3. Ép buộc lưu trữ có cấu trúc (Structured Memory Enforcement)
Thay vì để Agent trò chuyện phi cấu trúc, `pentestagent` bắt buộc Agent phải gọi Tool `notes` với schema xác thực nghiêm ngặt để cập nhật tri thức:

```text
- Structured Notes (CRITICAL): Your notes build a knowledge graph.
  - TARGET FIELD IS MANDATORY: For categories credential, vulnerability, and finding, you MUST include target="IP_ADDRESS".
  - Credentials (category="credential"): MUST have username + (password OR protocol), and target.
  - Host/Service Profiles (category="finding"): MUST have target + at least one of (services, endpoints, technologies, or port).
```

### 5.4. Xác thực chứng cứ thực thi (Deterministic Proof-of-Concept)
`Shannon` áp dụng triết lý "No Exploit, No Report" thông qua prompt chuyên biệt cho từng họ lỗ hổng:
- Phải tạo được payload thực thi cụ thể.
- Phải trích xuất được file PoC script chạy độc lập (curl hoặc python script).
- Không chấp nhận giả định hay suy đoán lý thuyết.

---

## 6. HỆ SINH THÁI TOOL, MÔI TRƯỜNG THỰC THI SANDBOX & CƠ CHẾ ẨN DANH

### 6.1. Ba cơ chế gọi công cụ (Tool Execution Mechanisms)
1. **Model Context Protocol (MCP)**:
   - Dẫn đầu bởi `hexstrike-ai`, `dot-hunter`, `strix`, `Dark-Moon`.
   - MCP chuẩn hóa cách Agent khám phá danh sách tool (`tools/list`) và thực thi tool (`tools/call`) qua giao thức JSON-RPC, độc lập hoàn toàn với ngôn ngữ lập trình của server.
2. **Subprocess / CLI Execution Sandbox**:
   - Phổ biến trong `strix`, `pentestagent`, `Decepticon`.
   - Lệnh được đóng gói và thực thi bên trong Docker container (như Kali Linux image) với giới hạn thời gian (timeout), CPU và bộ nhớ để tránh việc payload làm tê liệt máy chủ.
3. **Browser Automation Engine**:
   - Sử dụng **Playwright** (`Shannon`, `Strix`, `pentestagent`).
   - Rất quan trọng đối với web pentest: cho phép Agent tương tác trực tiếp với DOM, bypass CSRF token, bắt network requests, vượt CAPTCHA mô phỏng, và kích hoạt XSS DOM-based.

### 6.2. Cơ chế Bảo mật Dữ liệu & Ẩn danh (Privacy & OpSec)
Trong pentest thực tế cho doanh nghiệp, việc gửi endpoint nội bộ, API key hoặc PII khách hàng lên OpenAI/Anthropic là vi phạm hợp đồng bảo mật (NDA).
- **Giải pháp của `jfreemansh/Anonproxy`**:
  - Kiến trúc: Local Reverse Proxy đứng trước LLM API.
  - Thuật toán 3 bước:
    1. *Consistency Rescan*: Mọi giá trị nhạy cảm đã thấy trong phiên được ghi nhớ trong Vault (SQLite).
    2. *Single-Pass Longest-First Replacement*: Thay thế tất cả chuỗi nhạy cảm bằng token định danh một lần duy nhất theo thứ tự chuỗi dài nhất trước để tránh xung đột regex.
    3. *Tolerant Restorer*: Tự động phục hồi giá trị thật khi LLM trả về, bất kể LLM viết hoa, viết thường hoặc định dạng lại token.
- **Giải pháp của `ASCIT31/Dark-Moon`**:
  - Tích hợp Privacy Gateway kết hợp mô hình LLM cục bộ (Local LLM via Ollama) để xử lý dữ liệu nhạy cảm cao, chỉ gửi dữ liệu đã làm sạch lên Frontier Cloud LLM để phân tích logic phức tạp.

---

## 7. ĐÁNH GIÁ KHẢ NĂNG MỞ RỘNG (EXTENSIBILITY & SCALABILITY)

### 7.1. Khả năng bổ sung Agent mới (Modular Agent Addition)
- **Rất cao (Strix, Decepticon, PentestAgent)**: Chỉ cần định nghĩa một file prompt Persona (ví dụ `api_pentest.jinja`) và khai báo agent role trong registry.
- **Trung bình (PentAGI)**: Đòi hỏi viết struct và handler bằng Go, cấu hình lại migration SQL và biên dịch lại backend.

### 7.2. Khả năng mở rộng Công cụ (Tool Extensibility via MCP)
- Nhờ chuẩn **MCP**, việc thêm một công cụ mới (ví dụ: `wpscan`, `nuclei`, `semgrep`) không còn đòi hỏi sửa đổi core codebase của Agent:
  - Chỉ cần viết một script Python với decorator `@mcp.tool()` trong MCP server.
  - Agent tự động phát hiện tool schema mới trong phiên chạy kế tiếp.

### 7.3. Tối ưu hóa Chi phí Token (Token Budgeting & Cost Control)
- `strix` cài đặt lớp `TurnToolCallLimiter` và `SubagentBudgetReservedError` để chặn đứng tình trạng vòng lặp vô tận gây "cháy" tài khoản API.
- `pentagi` có cơ chế Adviser chống lặp giúp tiết kiệm 2–3 lần số lượng token so với chạy thô.

---

## 8. BẢNG SO SÁNH ĐỐI CHUẨN ĐA CHIỀU GIỮA CÁC HỆ THỐNG ĐẦU BẢNG

| Tiêu chí so sánh | Strix | Shannon | PentAGI | Decepticon | PentestAgent | HexStrike AI | Anonproxy |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Điểm sao GitHub** | ~69k | ~49k | ~31k | ~6.3k | ~3.1k | ~12.8k | ~8 |
| **Loại hình Pentest** | Black / Grey / White | White-box (Source Code) | Full Cycle (Black/Grey) | Red Team / Kill Chain | Black-box / Host | Tool MCP Server | Privacy Proxy |
| **Kiến trúc Agent** | Graph of Agents | Temporal Workflow | 10+ Multi-Agent | LangGraph StateGraph | ReAct / Crew | MCP Toolkit | Proxy Engine |
| **Bảo chứng PoC (No FP)** | Rất cao | **Tuyệt đối (100%)** | Trung bình | Cao | Khá | Không áp dụng | Không áp dụng |
| **Tự động vá lỗi (Fix)** | **Có (Find & Fix)** | Không | Không | Không | Không | Không | Không |
| **Tích hợp MCP** | Client | Không | Không | Server & Client | Client | **Full Server** | Không |
| **Bảo vệ Ẩn danh (OpSec)** | Có (Header strip) | Không | Không | Sandbox Kali | OpSec subagent | Không | **Chuyên biệt (100%)** |
| **Độ phức tạp cài đặt** | Cực thấp (1 curl) | Thấp (Node+Docker) | Trung bình (Docker) | Trung bình (Docker) | Thấp (uv / pip) | Thấp (pip) | Rất thấp (pip) |

---

## 9. KHUYẾN NGHỊ KIẾN TRÚC CHO ĐỒ ÁN PENTEST WEB/API AGENT TỐI ƯU

Dựa trên việc nghiên cứu trực tiếp mã nguồn của 63 dự án, để xây dựng một hệ thống Agent tự động pentest web app/API chất lượng cao cho đồ án tốt nghiệp hoặc dự án thực tế, đây là mô hình kiến trúc tối ưu nhất:

```mermaid
graph TD
    Client[Web UI / CLI Dashboard] --> Orchestrator[Root Orchestrator Agent]
    
    subgraph Privacy_Layer["1. Privacy & Anonymization Layer (Học từ Anonproxy)"]
        Orchestrator <--> AnonProxy[Two-way Reversible Anonymizer]
        AnonProxy <--> LLM[Frontier LLM: Claude 3.5 Sonnet / GPT-4o]
    end
    
    subgraph Agent_Core["2. Multi-Agent Engine (Học từ Strix & Decepticon)"]
        Orchestrator -->|Delegation| ReconAgent[Recon & Crawler Agent]
        Orchestrator -->|Delegation| VulnScanAgent[Vulnerability Scanner Agent]
        Orchestrator -->|Delegation| ExploitAgent[Exploit & PoC Verifier]
        Orchestrator -->|Delegation| PatchAgent[Remediation / Code-Fix Agent]
    end
    
    subgraph Execution_Env["3. Execution Sandbox via MCP (Học từ HexStrike & Shannon)"]
        ExploitAgent <--> MCP_Host[MCP Tool Server Manager]
        MCP_Host --> Docker[Kali Docker Sandbox: nmap, sqlmap, curl]
        MCP_Host --> Browser[Playwright Headless Browser: XSS, CSRF]
    end
    
    subgraph State_Memory["4. Structured Knowledge Memory (Học từ PentestAgent & PentAGI)"]
        ReconAgent --> GraphDB[(SQLite / Neo4j Target Knowledge Graph)]
        VulnScanAgent --> GraphDB
        ExploitAgent --> GraphDB
    end
```

### 4 Trụ cột thiết kế cốt lõi nên áp dụng:
1. **Lớp Ủy quyền Root-Worker (Strix pattern)**:
   - Root Agent chỉ nhận input từ người dùng, đọc scope, phân rã mục tiêu và sinh subagent. Tuyệt đối không để Root Agent chạy lệnh trực tiếp.
2. **Nguyên tắc "No Exploit, No Report" (Shannon pattern)**:
   - Mọi phát hiện lỗi tiềm năng phải có bước kiểm chứng PoC chạy được (qua script curl hoặc Playwright). Nếu PoC thất bại → loại bỏ hoặc hạ cấp cảnh báo để tránh báo động giả làm loãng báo cáo.
3. **Cơ chế Giao tiếp Tool qua MCP (HexStrike pattern)**:
   - Thay vì hardcode lệnh shell trong code Python, hãy tạo một MCP Server nội bộ chứa các tool: `run_curl`, `run_sqlmap`, `browser_navigate`, `inspect_dom`. Điều này giúp code cực kỳ sạch, dễ test và mở rộng.
4. **Bộ nhớ có cấu trúc & Chống lặp (PentestAgent & PentAGI pattern)**:
   - Ép buộc Subagent ghi nhận phát hiện dưới dạng đối tượng JSON/Pydantic vào cơ sở dữ liệu thay vì văn bản thuần. Cài đặt cơ chế đếm số lần thất bại (nếu một endpoint thử 3 lần không ra lỗi → tự động chuyển sang endpoint khác).

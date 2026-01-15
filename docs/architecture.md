# AgentForge Architecture

## System Overview

AgentForge is built on a **graph-based, stateful orchestration architecture** using LangGraph, with specialized agents coordinating through a MongoDB-backed memory layer and load-balanced LLM API calls.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST Server                      │
│                  (backend/server.py)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            LangGraph Orchestrator                           │
│        (backend/orchestrator_langgraph.py)                  │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   ││
│  │CEO+      │─▶│Developer │─▶│Writer    │─▶│Confidence│  ││
│  │Research  │  │(Key 2)   │  │(Key 3)   │  │(Key 1)   │  ││
│  │(Key 1)   │  │          │  │          │  │          │  ││
│  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘  ││
│                                                  │         │
│                                            ┌─────▼─────┐   │
│                                            │ Reviewer  │   │
│                                            │ (Key 2)   │   │
│                                            └─────┬─────┘   │
│                                                  │         │
│                                            ┌─────▼─────┐   │
│                                            │    END    │   │
│                                            └───────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Memory Layer       │
              │   (backend/memory.py)│
              │   MongoDB + Motor    │
              └──────────────────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
         ┌──────────┐      ┌──────────┐
         │Sessions  │      │Plans     │
         │Research  │      │Documents │
         │Actions   │      │Confidence│
         └──────────┘      └──────────┘
```

## Updated Workflow (v2.0)

**Complete Pipeline:**
```
CEO+Research → Developer → Writer → Confidence → Reviewer → END
   (Key 1)      (Key 2)    (Key 3)    (Key 1)    (Key 2)
```

### Key Features of v2.0:
- ✅ **Reviewer Agent Added**: Automatically repairs documents when confidence issues detected
- ✅ **Quality Validation**: Confidence agent evaluates before reviewer
- ✅ **API Key Distribution**: Load balanced across 3 keys
- ✅ **State Persistence**: All outputs saved to MongoDB
- ✅ **Error Recovery**: Reviewer can iterate until issues resolved

---

## Core Components

### 1. **API Layer** (`server.py`)
- **Technology**: FastAPI + Uvicorn (ASGI)
- **Purpose**: REST endpoint exposing agent workflows
- **Features**:
  - `/run` endpoint for executing agent pipelines
  - Pydantic request/response validation
  - Environment-based orchestrator selection (LangGraph vs legacy)
  - Windows-compatible event loop policy

**Key Code Structure**:
```python
@app.post("/run")
async def run(req: RunRequest):
    goal, email = parse_command(req)
    result = await orchestrator.run(goal, email)
    return JSONResponse(serialize_doc(result))
```

---

### 2. **Orchestration Layer** (`orchestrator_langgraph.py`)

**LangGraph State Machine**:
- **Nodes**: CEO+Research, Developer, Writer, Validation
- **Edges**: Sequential flow with 2-second delays between transitions
- **State**: PipelineState TypedDict with session_id, goal, plan, research, developer, writer, confidence

**Node Execution Pattern**:
```python
async def node_ceo_and_research(state: PipelineState) -> PipelineState:
    combined = await self.ceo.create_plan_and_research(goal, key_index=0)
    await self.memory.save_plan(state["session_id"], plan)
    return {"plan": plan, "research": research}
```

**State Transitions**:
1. Entry → CEO+Research (no delay)
2. CEO+Research → Developer (2s delay)
3. Developer → Writer (2s delay)
4. Writer → Validation (2s delay)
5. Validation → END

---

### 3. **Agent Layer** (`agents/`)

#### **Base Agent** (`base.py`)
```python
class BaseAgent:
    async def think(self, prompt: str, purpose: str = "generation", key_index: int | None = None):
        system = f"you are the {self.name} agent."
        return await call_llm(prompt, system, purpose=purpose, key_index=key_index)
```

#### **Agent Responsibilities**

| Agent | File | Purpose | API Key | Output |
|-------|------|---------|---------|--------|
| **CEO** | `ceo.py` | Strategic planning + initial research | Key 1 (index 0) | Plan + Research findings |
| **Developer** | `developer.py` | Technical artifacts (diagrams, architecture) | Key 2 (index 1) | Mermaid diagrams, outlines |
| **Writer** | `writer.py` | Final document generation | Key 3 (index 2) | Formatted report |
| **Confidence** | `confidence.py` | Quality validation (confidence + hallucination) | Key 1 (index 0) | Quality metrics |
| **Automation** | `automation.py` | Email delivery via Gmail SMTP | N/A | Email status |

---

### 4. **LLM Client Layer** (`llm_client.py`)

**Key Routing Strategy**:
```python
# Fixed key assignment per agent:
- Key 1 (index 0): CEO+Research, Confidence
- Key 2 (index 1): Developer
- Key 3 (index 2): Writer

# Strategy: rotation (round-robin across all keys)
GROQ_KEY_STRATEGY=rotation
### 4. **Confidence Agent** (`agents/confidence.py`)
- **Role**: Quality validation & hallucination detection
- **Key Index**: 0 (Key 1)
- **Input**: Writer's document
- **Output**: Confidence metrics and issue detection
- **Integration**: Runs after Writer, before Reviewer

---

### 5. **Reviewer Agent** (`agents/reviewer.py`)
- **Role**: Autonomous issue repair & document refinement
- **Key Index**: 1 (Key 2)
- **Input**: Document + detected issues from Confidence agent
- **Output**: Revised document with fixes applied
- **Logic**: Reads hallucination issues, targets repairs
- **Integration**: Runs after Confidence check, returns to END

---

### 6. **Automation Agent** (`agents/automation.py`)
- **Role**: Email delivery
- **Key Index**: None (no LLM calls)
- **Input**: Email target, subject, body
- **Output**: Email send confirmation
- **Tool**: `tools/gmail_tool.py` (SMTP)

---

## Agent Pipeline States

### State Transitions with 2-Second Delays:
```
START → CEO+Research (0s) 
      → [2s delay] → Developer 
      → [2s delay] → Writer 
      → [2s delay] → Confidence 
      → [2s delay] → Reviewer 
      → END
```

**Why Delays?**
- Prevents rapid successive API calls
- Simulates logical processing time
- Reduces 429 rate limit errors
- Improves user experience (shows progress)

---

## API Key Distribution

| Agent | API Key | Calls/Report |
|-------|---------|--------------|
| CEO+Research | Key 1 (GROQ_API_KEY) | 1 (combined) |
| Developer | Key 2 (GROQ_API_KEY_2) | 1 |
| Writer | Key 3 (GROQ_API_KEY_3) | 1 |
| Confidence | Key 1 (GROQ_API_KEY) | 1 (combined) |
| Reviewer | Key 2 (GROQ_API_KEY_2) | 1 |
| **Total** | | **5 calls** |

**Load Balancing:**
- Key 1: CEO+Research, Confidence (2 calls)
- Key 2: Developer, Reviewer (2 calls)
- Key 3: Writer (1 call)
- **Ratio**: 2:2:1 distribution for optimal rate limit handling

**MongoDB Collections**:
- `sessions`: User requests and metadata
- `plans`: Agent task breakdowns
- `research`: Research findings
- `documents`: Generated content
- `actions`: Email sends, confidence reports

**Async Pattern**:
```python
class MemoryStore:
    def __init__(self, mongo_uri: str):
        self.client = AsyncIOMotorClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
        self.db = self.client["AgentForge"]
    
    async def save_plan(self, session_id: str, plan: Dict):
        plan["session_id"] = session_id
        plan["created_at"] = datetime.now()
        await self.db.plans.insert_one(plan)
```

---

## Design Patterns

### 1. **State Machine Pattern** (LangGraph)
- Explicit state transitions
- Conditional routing based on quality metrics
- Idempotent node execution

### 2. **Repository Pattern** (Memory)
- Abstract data persistence
- Swap MongoDB for any async-compatible store
- Session-based context isolation

### 3. **Strategy Pattern** (LLM Routing)
- Pluggable key selection strategies
- Fixed routing per agent (current)
- Round-robin rotation (configurable)

### 4. **Factory Pattern** (Agent Creation)
- Centralized agent instantiation in orchestrator
- Dependency injection (memory layer)

---

## Data Flow

### Typical Request Flow:
```
1. POST /run {"goal": "Write supply chain proposal"}
   └→ server.py validates request

2. Orchestrator creates session in MongoDB
   └→ Initializes PipelineState

3. Node: CEO+Research (Key 1)
   ├→ LLM generates plan + research
   └→ Saves to MongoDB

4. Node: Developer (Key 2, +2s delay)
   ├→ Reads research from state
   ├→ LLM generates technical artifacts
   └→ Updates state

5. Node: Writer (Key 3, +2s delay)
   ├→ Reads research + developer output
   ├→ LLM generates final document
   └→ Saves to MongoDB

6. Node: Validation (Key 1, +2s delay)
   ├→ LLM evaluates confidence + hallucination
   └→ Saves quality report

7. Response assembly
   ├→ Formats email (if enabled)
   ├→ Prints metrics to console
   └→ Returns JSON with all artifacts
```

---

## Scalability & Performance

### Current Optimizations:
- **API Call Reduction**: 4 calls per report (67% reduction from 12-call baseline)
- **Combined Operations**: CEO+Research (1 call), Confidence+Hallucination (1 call)
- **Async I/O**: All operations non-blocking (FastAPI, Motor, httpx)
- **Pacing**: 0.4s global interval + 2s state transition delays

### Scalability Considerations:
- **Horizontal**: Multiple server instances with shared MongoDB
- **Vertical**: LLM concurrency controlled by semaphore (current: 1)
- **Database**: MongoDB sharding for high session volumes
- **Caching**: Add Redis for frequently accessed plans/research

---

## Security & Configuration

### Environment Variables:
```env
# Core
USE_LANGGRAPH=true
APP_HOST=0.0.0.0
APP_PORT=8000

# LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_KEY_2=your_second_api_key_here
GROQ_API_KEY_3=your_third_api_key_here
GROQ_KEY_STRATEGY=rotation
GROQ_MIN_INTERVAL_SECONDS=0.4

# Database
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname

# Email (optional)
EMAIL_ENABLED=true
ALLOW_EMAIL_SENDING=true
GMAIL_APP_PASSWORD=your_gmail_app_password
```

### Security Best Practices:
- ✅ API keys in environment variables (never committed)
- ✅ MongoDB TLS with certifi CA bundle
- ✅ HTTPS for external API calls
- ✅ Email sending requires dual flags (EMAIL_ENABLED + ALLOW_EMAIL_SENDING)
- ✅ Input validation via Pydantic

---

## Extension Points

### Adding a New Agent:
1. Create `agents/new_agent.py` extending `BaseAgent`
2. Implement `async def execute(self, task: str, key_index: int | None = None)`
3. Add node to LangGraph in `orchestrator_langgraph.py`
4. Wire edges and assign API key index

### Adding a New LLM Provider:
1. Add provider logic in `llm_client.py:_call_with_provider()`
2. Add configuration in `config.py`
3. Update key selection logic if needed

### Custom Quality Gates:
1. Modify `route_after_validation()` in orchestrator
2. Add conditional edges based on confidence thresholds
3. Implement retry loop if needed

---

## Monitoring & Observability

### Built-in Logging:
- **Console**: Quality metrics printed after validation
- **MongoDB**: All actions, plans, documents persisted
- **Response**: Session ID for tracking

### Recommended Additions:
- Structured logging (loguru)
- APM (Datadog, New Relic)
- Prometheus metrics export
- OpenTelemetry tracing

---

## References

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Motor (Async MongoDB)**: https://motor.readthedocs.io/
- **Groq API**: https://console.groq.com/docs

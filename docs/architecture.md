# AgentForge Architecture

## System Overview

AgentForge is built on a **graph-based, stateful orchestration architecture** using LangGraph, with specialized agents coordinating through a MongoDB-backed memory layer and load-balanced LLM API calls.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST Server                      │
│                      (server.py)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            LangGraph Orchestrator                           │
│          (orchestrator_langgraph.py)                        │
│                                                             │
│  ┌──────────┐    ┌──────────┐   ┌──────────┐    ┌──────────┐│
│  │CEO+      │──▶│Developer │──▶│Writer    │──▶│Validation││
│  │Research  │    │(Key 2)   │   │(Key 3)   │    │(Key 1)   ││
│  │(Key 1)   │    │          │   │          │    │          ││
│  └──────────┘    └──────────┘   └──────────┘    └──────────┘│
│       │              │              │              │        │
│       └──────────────┴──────────────┴──────────────┘        │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Memory Layer       │
              │   (memory.py)        │
              │   MongoDB + Motor    │
              └──────────────────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
         ┌──────────┐      ┌──────────┐
         │Sessions  │      │Plans     │
         │Research  │      │Documents │
         │Actions   │      │          │
         └──────────┘      └──────────┘
```

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
GROQ_MIN_INTERVAL_SECONDS=0.4  # Global pacing
```

**SSL Certificate Handling**:
```python
async with httpx.AsyncClient(timeout=30, verify=certifi.where()) as client:
    response = await client.post(url, headers=headers, json=body)
```

---

### 5. **Memory Layer** (`memory.py`)

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
- **Load Balancing**: 3-key rotation with fixed routing prevents rate limits
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

# LLM (3 keys for load balancing)
GROQ_API_KEY=gsk_...
GROQ_API_KEY_2=gsk_...
GROQ_API_KEY_3=gsk_...
GROQ_KEY_STRATEGY=rotation
GROQ_MIN_INTERVAL_SECONDS=0.4

# Database
MONGO_URI=mongodb+srv://...

# Email (optional)
EMAIL_ENABLED=true
ALLOW_EMAIL_SENDING=true
GMAIL_APP_PASSWORD=...
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

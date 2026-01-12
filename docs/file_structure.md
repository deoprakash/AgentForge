# File Structure Documentation

## Directory Overview

```
AgenticAI/
├── config.py                     # Environment configuration loader
├── llm_client.py                 # Unified LLM API client
├── memory.py                     # MongoDB async persistence layer
├── orchestrator_langgraph.py     # LangGraph-based pipeline orchestrator
├── server.py                     # FastAPI REST API server
├── test.py                       # Testing/debugging utilities
├── utils.py                      # Shared utilities (parsing, serialization)
├── pyproject.toml                # Poetry project metadata
├── requirements.txt              # Pip dependencies (generated from Poetry)
├── README.md                     # Project documentation
├── .env                          # Environment variables (not in repo)
├── .gitignore                    # Git ignore rules
│
├── agents/                       # Agent implementations
│   ├── __init__.py              # Agent module exports
│   ├── base.py                  # BaseAgent abstract class
│   ├── ceo.py                   # CEO agent (planning + research)
│   ├── developer.py             # Developer agent (technical artifacts)
│   ├── writer.py                # Writer agent (document generation)
│   ├── confidence.py            # Confidence agent (quality validation)
│   ├── automation.py            # Automation agent (email delivery)
│   └── __pycache__/             # Python bytecode cache
│
├── tools/                        # External tool integrations
│   ├── __init__.py              # Tool module exports
│   ├── search_tool.py           # Web search via SerpAPI (unused)
│   ├── gmail_tool.py            # Gmail SMTP client
│   ├── calendar_tool.py         # Google Calendar API (unused)
│   ├── file_tool.py             # File system operations (unused)
│   └── __pycache__/             # Python bytecode cache
│
├── outputs/                      # Generated artifacts (gitignored)
│   └── diagram.mmd              # Example Mermaid diagram output
│
├── docs/                         # Project documentation
│   ├── architecture.md          # System design and components
│   ├── workflows.md             # Execution flow diagrams
│   ├── file_structure.md        # This file
│   ├── tech_stack.md            # Technology dependencies
│   ├── troubleshooting.md       # Common issues and solutions
│   └── api_reference.md         # REST API documentation
│
└── __pycache__/                  # Python bytecode cache
```

---

## Core Files

### `config.py`
**Purpose**: Centralized configuration management  
**Dependencies**: `python-dotenv`, `os`  
**Key Exports**:
- `GROQ_API_KEY`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3`
- `GROQ_KEY_STRATEGY` (rotation/sequential/random)
- `GROQ_MIN_INTERVAL_SECONDS` (rate limit pacing)
- `MONGO_URI` (MongoDB connection string)
- `USE_LANGGRAPH` (orchestrator selection flag)
- `EMAIL_ENABLED`, `ALLOW_EMAIL_SENDING` (email flags)
- `GMAIL_APP_PASSWORD`, `GMAIL_USER` (SMTP credentials)

**Usage Pattern**:
```python
from config import GROQ_API_KEY, USE_LANGGRAPH

if USE_LANGGRAPH:
    orchestrator = OrchestratorLangGraph(...)
```

**Critical Settings**:
- All API keys validated on import (raises error if missing)
- `USE_LANGGRAPH=true` enables graph-based orchestration
- Email requires BOTH flags enabled + valid SMTP credentials

---

### `llm_client.py`
**Purpose**: Unified interface for LLM API calls  
**Dependencies**: `httpx`, `certifi`, `config`  
**Key Functions**:

#### `async def call_llm(prompt: str, system: str, purpose: str = "generation", key_index: int | None = None) -> str`
- **Description**: Main LLM invocation function
- **Parameters**:
  - `prompt`: User message
  - `system`: System prompt (agent role)
  - `purpose`: "generation" (temp 0.7) or "validation" (temp 0.3)
  - `key_index`: Force specific key (0=Key1, 1=Key2, 2=Key3, None=auto-select)
- **Returns**: LLM response text
- **Error Handling**: Retries once on 429, raises on 5xx

#### `def _get_next_groq_key() -> tuple[str, int]`
- **Description**: Key selection based on strategy
- **Strategy Modes**:
  - `rotation`: Round-robin across all keys
  - `sequential`: Use keys in order
  - `random`: Random selection
- **Returns**: (api_key, key_index)

**Rate Limiting**:
```python
# Global pacing enforcement
last_call = _last_call_times.get(selected_key, 0)
elapsed = time.time() - last_call
if elapsed < GROQ_MIN_INTERVAL_SECONDS:
    await asyncio.sleep(GROQ_MIN_INTERVAL_SECONDS - elapsed)
```

**SSL Configuration**:
```python
async with httpx.AsyncClient(timeout=30, verify=certifi.where()) as client:
    # Uses system CA bundle via certifi
```

---

### `memory.py`
**Purpose**: Async MongoDB persistence layer  
**Dependencies**: `motor`, `pymongo`, `certifi`  
**Class**: `MemoryStore`

**Key Methods**:

| Method | Purpose | Collection |
|--------|---------|------------|
| `save_session()` | Store initial request | `sessions` |
| `save_plan()` | Store CEO plan | `plans` |
| `save_research()` | Store research findings | `research` |
| `save_document()` | Store final document | `documents` |
| `save_action()` | Log email/validation | `actions` |
| `get_session()` | Retrieve session data | `sessions` |
| `get_latest_plan()` | Get most recent plan | `plans` |

**Connection Pattern**:
```python
self.client = AsyncIOMotorClient(
    mongo_uri,
    tls=True,
    tlsCAFile=certifi.where()  # SSL certificate validation
)
self.db = self.client["AgentForge"]
```

**Data Model**:
- All documents include `session_id` (foreign key)
- Timestamps in UTC: `created_at`, `updated_at`
- ObjectId primary keys (`_id`)

---

### `orchestrator_langgraph.py`
**Purpose**: LangGraph-based pipeline orchestration  
**Dependencies**: `langgraph`, `typing`, `agents.*`, `memory`  
**Class**: `OrchestratorLangGraph`

**State Definition**:
```python
class PipelineState(TypedDict):
    session_id: str
    goal: str
    plan: List[Dict] | None
    research: str | None
    developer: str | None
    writer: str | None
    confidence: Dict | None
```

**Graph Construction**:
```python
graph = StateGraph(PipelineState)

# Node registration
graph.add_node("ceo_and_research", node_ceo_and_research)
graph.add_node("developer", node_developer)
graph.add_node("writer", node_writer)
graph.add_node("validation", node_validation)

# Edge wiring
graph.set_entry_point("ceo_and_research")
graph.add_edge("ceo_and_research", "developer")
graph.add_edge("developer", "writer")
graph.add_edge("writer", "validation")
graph.add_edge("validation", END)

# Compile
runnable = graph.compile()
```

**Node Implementation Pattern**:
```python
async def node_developer(state: PipelineState) -> PipelineState:
    await asyncio.sleep(2)  # State transition delay
    research = state["research"]
    result = await self.developer.execute(research, key_index=1)
    return {"developer": result}
```

**Key Routing**:
- Node 1 (CEO+Research): `key_index=0` (Key 1)
- Node 2 (Developer): `key_index=1` (Key 2)
- Node 3 (Writer): `key_index=2` (Key 3)
- Node 4 (Validation): `key_index=0` (Key 1)

---

### `server.py`
**Purpose**: FastAPI REST API server  
**Dependencies**: `fastapi`, `uvicorn`, `pydantic`  
**Key Components**:

#### Request Model:
```python
class RunRequest(BaseModel):
    command: str  # Natural language command with goal + optional email
```

#### Main Endpoint:
```python
@app.post("/run")
async def run(req: RunRequest):
    goal, email = parse_command(req.command)
    result = await orchestrator.run(goal, email)
    
    # Print quality metrics
    if result.get("confidence"):
        print(f"Confidence Score: {result['confidence']['confidence_score']}%")
        print(f"Hallucination Risk: {result['confidence']['hallucination_risk']}")
    
    return JSONResponse(serialize_doc(result))
```

#### Windows Compatibility:
```python
if __name__ == "__main__":
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    uvicorn.run(
        app,
        host=APP_HOST,
        port=APP_PORT,
        reload=False  # Disabled on Windows to prevent stdin errors
    )
```

---

### `utils.py`
**Purpose**: Shared utility functions  
**Dependencies**: `re`, `bson`, `datetime`

**Key Functions**:

#### `parse_command(cmd: str) -> tuple[str, str | None]`
```python
# Extracts goal and email from natural language
# Example: "Write proposal, send to john@example.com"
# Returns: ("Write proposal", "john@example.com")
```

#### `serialize_doc(doc: dict) -> dict`
```python
# Converts MongoDB ObjectId to string for JSON serialization
# Handles nested dicts and lists recursively
```

---

## Agents Module

### `agents/base.py`
**Purpose**: Abstract base class for all agents  
**Class**: `BaseAgent`

**Key Method**:
```python
async def think(self, prompt: str, purpose: str = "generation", key_index: int | None = None) -> str:
    system = f"you are the {self.name} agent."
    return await call_llm(prompt, system, purpose=purpose, key_index=key_index)
```

**Subclass Pattern**:
```python
class MyAgent(BaseAgent):
    def __init__(self, name: str = "MyAgent"):
        super().__init__(name)
    
    async def execute(self, task: str, key_index: int | None = None) -> str:
        prompt = f"Task: {task}\nProvide: ..."
        return await self.think(prompt, key_index=key_index)
```

---

### `agents/ceo.py`
**Purpose**: Strategic planning and initial research  
**Class**: `CEOAgent` (extends `BaseAgent`)

**Key Method**:
```python
async def create_plan_and_research(self, goal: str, key_index: int | None = None) -> tuple[List[Dict], str]:
    prompt = f"""
    Goal: {goal}
    
    Return JSON:
    {{
      "plan": [
        {{"step": 1, "task": "...", "description": "..."}},
        ...
      ],
      "research": "Comprehensive research findings..."
    }}
    """
    response = await self.think(prompt, key_index=key_index)
    data = json.loads(response)
    return data["plan"], data["research"]
```

**Output**:
- Plan: Array of task objects with steps
- Research: Multi-paragraph research findings

---

### `agents/developer.py`
**Purpose**: Technical artifact generation  
**Class**: `DeveloperAgent` (extends `BaseAgent`)

**Output Types**:
- Mermaid diagrams (flowcharts, sequence diagrams, architecture)
- Technical specifications
- Implementation checklists
- System architecture outlines

**Example Prompt**:
```python
prompt = f"""
Based on: {research}

Generate:
1. Mermaid diagram showing workflow
2. Technical architecture outline
3. Technology stack recommendations
"""
```

---

### `agents/writer.py`
**Purpose**: Final document/report generation  
**Class**: `WriterAgent` (extends `BaseAgent`)

**Output**:
- Formal proposals
- Technical reports
- Executive summaries
- Multi-section documents (500+ words)

**Inputs Used**:
- Original goal
- Research findings
- Developer technical artifacts

---

### `agents/confidence.py`
**Purpose**: Quality validation (combined confidence + hallucination)  
**Class**: `ConfidenceAgent` (extends `BaseAgent`)

**Key Method**:
```python
async def evaluate_and_store(self, goal: str, document: str, session_id: str, key_index: int | None = None) -> Dict:
    prompt = f"""
    Goal: {goal}
    Document: {document[:500]}...
    
    Evaluate and return JSON:
    {{
      "confidence_score": 0-100,
      "confidence_reasoning": "...",
      "hallucination_risk": "low|medium|high",
      "hallucination_reasoning": "..."
    }}
    """
    response = await self.think(prompt, purpose="validation", key_index=key_index)
    metrics = json.loads(response)
    
    # Store in MongoDB actions collection
    await self.memory.save_action(session_id, {
        "type": "confidence_report",
        ...metrics
    })
    
    return metrics
```

**Validation Criteria**:
- **Confidence**: Goal alignment, completeness, structure
- **Hallucination**: Factual accuracy, supported claims, no fabrication

---

### `agents/automation.py`
**Purpose**: Email delivery automation  
**Class**: `AutomationAgent` (extends `BaseAgent`)

**Dependencies**: `tools.gmail_tool.GmailTool`

**Key Method**:
```python
async def send_email(self, to: str, subject: str, body: str, session_id: str):
    if not ALLOW_EMAIL_SENDING:
        return
    
    self.gmail.send_email(to, subject, body)
    
    await self.memory.save_action(session_id, {
        "type": "email_sent",
        "to": to,
        "subject": subject,
        "timestamp": datetime.now()
    })
```

---

## Tools Module

### `tools/gmail_tool.py`
**Purpose**: Gmail SMTP email sending  
**Class**: `GmailTool`

**Configuration**:
```python
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS
username = GMAIL_USER  # from config
password = GMAIL_APP_PASSWORD  # App-specific password
```

**Security Note**: Requires Gmail App Password (not account password)

---

### Unused Tools (Available for Extension)
- `tools/search_tool.py`: SerpAPI web search integration
- `tools/calendar_tool.py`: Google Calendar API wrapper
- `tools/file_tool.py`: Local file system operations

---

## Configuration Files

### `.env` (Not in Repository)
```env
# LLM Configuration
GROQ_API_KEY=gsk_...
GROQ_API_KEY_2=gsk_...
GROQ_API_KEY_3=gsk_...
GROQ_KEY_STRATEGY=rotation
GROQ_MIN_INTERVAL_SECONDS=0.4

# Database
MONGO_URI=mongodb+srv://...

# Orchestration
USE_LANGGRAPH=true

# Server
APP_HOST=0.0.0.0
APP_PORT=8000

# Email
EMAIL_ENABLED=true
ALLOW_EMAIL_SENDING=true
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

### `pyproject.toml`
**Purpose**: Poetry project definition  
**Key Sections**:
- `[tool.poetry.dependencies]`: Runtime deps
- `[tool.poetry.dev-dependencies]`: Dev-only deps
- `[build-system]`: Poetry build backend config

### `requirements.txt`
**Purpose**: Pip-compatible dependency list  
**Generated From**: `poetry export -f requirements.txt`

---

## Dependency Graph

```
server.py
├── config.py
├── utils.py
├── orchestrator_langgraph.py
│   ├── langgraph
│   ├── memory.py
│   │   └── motor (MongoDB)
│   └── agents/
│       ├── base.py
│       │   └── llm_client.py
│       │       ├── httpx
│       │       ├── certifi
│       │       └── config.py
│       ├── ceo.py
│       ├── developer.py
│       ├── writer.py
│       ├── confidence.py
│       └── automation.py
│           └── tools/gmail_tool.py
```

---

## File Import Patterns

### Absolute Imports (Preferred)
```python
from config import GROQ_API_KEY
from agents.ceo import CEOAgent
from tools.gmail_tool import GmailTool
```

### Relative Imports (Within Modules)
```python
# In agents/ceo.py
from .base import BaseAgent
```

---

## Output Artifacts

### `outputs/diagram.mmd`
**Purpose**: Example Mermaid diagram generated by Developer agent  
**Format**: Mermaid markdown syntax  
**Usage**: Can be rendered with Mermaid CLI or online editor

---

## Cache Directories

### `__pycache__/`
**Purpose**: Python bytecode compilation cache  
**Location**: Root, `agents/`, `tools/`  
**Git Status**: Ignored via `.gitignore`

---

## Documentation Files

### `docs/architecture.md`
- System design overview
- Component descriptions
- LangGraph state machine
- Data flow diagrams

### `docs/workflows.md`
- Execution flow step-by-step
- Timing analysis
- API call breakdown
- Error handling patterns

### `docs/file_structure.md`
- This file
- Directory tree
- File purposes
- Dependency relationships

### `docs/tech_stack.md`
- Complete dependency list with versions
- Technology choices rationale
- Performance characteristics

### `docs/troubleshooting.md`
- Common errors
- Solutions and fixes
- Debugging strategies

### `docs/api_reference.md`
- REST endpoint documentation
- Request/response schemas
- Example curl commands

---

## File Naming Conventions

- **Modules**: `snake_case.py` (e.g., `llm_client.py`)
- **Classes**: `PascalCase` (e.g., `CEOAgent`, `MemoryStore`)
- **Functions**: `snake_case` (e.g., `parse_command`, `call_llm`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `GROQ_API_KEY`, `USE_LANGGRAPH`)

---

## Version Control

### `.gitignore` Patterns
```
__pycache__/
*.pyc
.env
outputs/
.venv/
.pytest_cache/
*.log
```

---

## Future File Structure

### Potential Additions:
```
tests/
├── test_agents.py
├── test_orchestrator.py
└── test_llm_client.py

logs/
├── api_calls.log
├── errors.log
└── performance.log

scripts/
├── setup.sh
└── deploy.py
```

---

## References

- [Architecture Documentation](architecture.md)
- [Workflow Details](workflows.md)
- [Technology Stack](tech_stack.md)

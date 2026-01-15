# System Dependencies & Connections

This document visualizes how all files and folders in AgentForge are interconnected, showing import relationships, data flow, and component dependencies.

---

## 📊 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         External World                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ HTTP Client  │    │   MongoDB    │    │  Groq API    │     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
└─────────┼────────────────────┼────────────────────┼─────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend Application                        │
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │  server.py   │────────▶│  config.py  │                      │
│  └──────┬───────┘         └──────┬───────┘                      │
│         │                        │                              │
│         │                        ▼                              │
│         │              ┌──────────────────┐                     │
│         │              │ llm_client.py    │◀───────┐           │
│         │              └─────────┬────────┘        │            │
│         │                        │                 │            │
│         ▼                        │                 │            │
│  ┌──────────────────────┐        │                 │            │
│  │ orchestrator_        │        │                 │            │
│  │ langgraph.py         │───────┼──────────────────┘            │
│  └──────┬───────────────┘       │                               │
│         │                        │                              │
│         │    ┌───────────────────┼──────────────┐               │
│         │    │                   │              │               │
│         ▼    ▼                   ▼              ▼               │
│    ┌─────────────┐      ┌──────────────┐  ┌─────────────┐       │
│    │ memory.py   │      │  agents/     │  │  utils.py   │       │
│    └─────────────┘      │   base.py    │  └─────────────┘       │
│                         └──────┬───────┘                        │
│                                │                                │
│         ┌──────────────────────┼───────────────────────┐        │
│         │          │           │           │           │        │
│         ▼          ▼           ▼           ▼           ▼        │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐     │
│    │ ceo.py │ │dev.py  │ │writer  │ │confidence│ │reviewer│     │
│    └────────┘ └────────┘ └────────┘ └──────────┘ └────────┘     │
│         │          │           │           │           │        │
│         └──────────┴───────────┴───────────┴───────────┘        │
│                                │                                │
│                                ▼                                │
│                         ┌─────────────┐                         │
│                         │ automation  │                         │
│                         │   .py       │                         │
│                         └──────┬──────┘                         │
│                                │                                │
│                                ▼                                │
│                         ┌─────────────┐                         │
│                         │   tools/    │                         │
│                         │ gmail_tool  │                         │
│                         └─────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 File-by-File Connection Map

### 1. **server.py** (Entry Point)

**Imports:**
```python
from config import APP_HOST, APP_PORT, MONGO_URI, LLM_PROVIDER, USE_LANGGRAPH
from orchestrator_langgraph import LangGraphOrchestrator
from memory import MemoryStore
from utils import serialize_doc, parse_command
```

**Connects To:**
- `config.py` → Environment configuration
- `orchestrator_langgraph.py` → Main workflow orchestrator
- `memory.py` → Database persistence
- `utils.py` → Helper functions

**Purpose:** HTTP server entry point, handles REST API requests

---

### 2. **config.py** (Configuration Hub)

**Imports:**
```python
from dotenv import load_dotenv
import os
```

**Used By:**
- `server.py` → Server settings (HOST, PORT)
- `llm_client.py` → API keys (GROQ_API_KEY_1/2/3)
- `memory.py` → Database URI (MONGO_URI)
- `orchestrator_langgraph.py` → Feature flags (USE_LANGGRAPH)
- `agents/automation.py` → Email settings (GMAIL_USER, GMAIL_APP_PASSWORD)

**Purpose:** Central configuration, loads .env variables

---

### 3. **orchestrator_langgraph.py** (Orchestration Core)

**Imports:**
```python
from langgraph.graph import StateGraph, END
from agents.ceo import CEOAgent
from agents.research import ResearchAgent
from agents.developer import DeveloperAgent
from agents.writer import WriterAgent
from agents.confidence import ConfidenceAgent
from agents.reviewer import ReviewerAgent
from agents.automation import AutomationAgent
from memory import MemoryStore
from utils import format_email_content
```

**Connects To:**
- `agents/` → All agent implementations
- `memory.py` → Session & state persistence
- `utils.py` → Email formatting

**Called By:**
- `server.py` → Executes workflows

**Purpose:** LangGraph state machine, coordinates agent execution

**Key Methods:**
- `_build_graph()` → Constructs agent pipeline
- `run()` → Executes complete workflow

---

### 4. **memory.py** (Data Persistence)

**Imports:**
```python
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from config import MONGO_URI (implicitly used)
```

**Connects To:**
- MongoDB (external) → Database storage

**Used By:**
- `orchestrator_langgraph.py` → Saves plans, research, documents
- `agents/confidence.py` → Saves quality reports
- `agents/automation.py` → Logs email sends

**Purpose:** Async MongoDB interface for state persistence

**Collections:**
- `sessions` → User requests
- `plans` → Task breakdowns
- `research` → Research findings
- `documents` → Generated content
- `actions` → Agent actions (emails, validations)

---

### 5. **llm_client.py** (LLM Gateway)

**Imports:**
```python
import httpx
import certifi
from config import GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3
```

**Connects To:**
- Groq API (external) → LLM inference
- `config.py` → API keys

**Used By:**
- `agents/base.py` → All agents inherit LLM access

**Purpose:** Unified LLM API client with multi-key routing

**Key Functions:**
- `call_llm()` → Main LLM invocation
- `_get_next_groq_key()` → Key selection strategy

---

### 6. **utils.py** (Utility Functions)

**Imports:**
```python
import re
from bson import ObjectId
from datetime import datetime
```

**Used By:**
- `server.py` → Parse commands, serialize responses
- `orchestrator_langgraph.py` → Format email content

**Purpose:** Helper functions for parsing and serialization

**Key Functions:**
- `parse_command()` → Extract goal from natural language
- `serialize_doc()` → Convert MongoDB documents to JSON
- `format_email_content()` → Format documents for email

---

## 🤖 Agent Connection Hierarchy

```
agents/base.py (Abstract Base)
    │
    ├─▶ agents/ceo.py
    │      └─▶ Uses: llm_client.py (Key 1)
    │
    ├─▶ agents/research.py
    │      └─▶ Uses: llm_client.py (Key 1)
    │
    ├─▶ agents/developer.py
    │      └─▶ Uses: llm_client.py (Key 2)
    │
    ├─▶ agents/writer.py
    │      └─▶ Uses: llm_client.py (Key 3)
    │
    ├─▶ agents/confidence.py
    │      ├─▶ Uses: llm_client.py (Key 1)
    │      └─▶ Uses: memory.py (save quality reports)
    │
    ├─▶ agents/reviewer.py ⭐
    │      └─▶ Uses: llm_client.py (Key 2)
    │
    └─▶ agents/automation.py
           └─▶ Uses: tools/gmail_tool.py
```

### Agent Base Class (`agents/base.py`)

**Imports:**
```python
from llm_client import call_llm
```

**Purpose:** Provides `think()` method for all agents

**Inherited By:** All agents (CEO, Research, Developer, Writer, Confidence, Reviewer, Automation)

---

### Individual Agents

#### **agents/ceo.py**
- **Extends:** `BaseAgent`
- **Key Index:** 0 (API Key 1)
- **Method:** `create_plan_and_research()`
- **Output:** Plan + Research (combined call)

#### **agents/research.py**
- **Extends:** `BaseAgent`
- **Key Index:** 0 (API Key 1)
- **Method:** `investigate()`
- **Output:** Research findings

#### **agents/developer.py**
- **Extends:** `BaseAgent`
- **Key Index:** 1 (API Key 2)
- **Method:** `generate_diagram()`
- **Output:** Mermaid diagrams, technical specs

#### **agents/writer.py**
- **Extends:** `BaseAgent`
- **Key Index:** 2 (API Key 3)
- **Method:** `write_document()`
- **Output:** Formatted proposals/reports

#### **agents/confidence.py**
- **Extends:** `BaseAgent`
- **Key Index:** 0 (API Key 1)
- **Method:** `evaluate_and_store()`
- **Output:** Confidence scores, hallucination risk, issues list
- **Side Effect:** Saves report to MongoDB

#### **agents/reviewer.py** ⭐
- **Extends:** `BaseAgent`
- **Key Index:** 1 (API Key 2)
- **Method:** `repair()`
- **Input:** Original document + detected issues
- **Output:** Revised document with fixes
- **Purpose:** Autonomous quality repair

#### **agents/automation.py**
- **Extends:** `BaseAgent`
- **Key Index:** None (no LLM calls)
- **Method:** `send_output()`
- **Uses:** `tools/gmail_tool.py`
- **Output:** Email delivery confirmation

---

## 🔄 Data Flow Through Pipeline

### Sequential Execution Flow

```
1. HTTP Request → server.py
         │
         ▼
2. Parse Command → utils.py
         │
         ▼
3. Create Session → memory.py
         │
         ▼
4. Initialize State → orchestrator_langgraph.py
         │
         ▼
5. Execute Pipeline:
   
   ┌─────────────────────────────────────────────┐
   │ Node: CEO + Research (Key 1)                │
   │  ├─▶ agents/ceo.py                          │
   │  │    └─▶ llm_client.py → Groq API          │
   │  └─▶ memory.py.save_plan()                  │
   └──────────────┬──────────────────────────────┘
                  │ [2s delay]
                  ▼
   ┌─────────────────────────────────────────────┐
   │ Node: Developer (Key 2)                     │
   │  ├─▶ agents/developer.py                    │
   │  │    └─▶ llm_client.py → Groq API          │
   │  └─▶ State Update                           │
   └──────────────┬──────────────────────────────┘
                  │ [2s delay]
                  ▼
   ┌─────────────────────────────────────────────┐
   │ Node: Writer (Key 3)                        │
   │  ├─▶ agents/writer.py                       │
   │  │    └─▶ llm_client.py → Groq API          │
   │  └─▶ memory.py.save_document()              │
   └──────────────┬──────────────────────────────┘
                  │ [2s delay]
                  ▼
   ┌─────────────────────────────────────────────┐
   │ Node: Confidence (Key 1)                    │
   │  ├─▶ agents/confidence.py                   │
   │  │    ├─▶ llm_client.py → Groq API          │
   │  │    └─▶ memory.py.save_action()           │
   │  └─▶ State Update (confidence metrics)      │
   └──────────────┬──────────────────────────────┘
                  │ [2s delay]
                  ▼
   ┌─────────────────────────────────────────────┐
   │ Node: Reviewer (Key 2) ⭐                    │
   │  ├─▶ agents/reviewer.py                     │
   │  │    └─▶ llm_client.py → Groq API          │
   │  └─▶ memory.py.save_document() (revised)    │
   └──────────────┬──────────────────────────────┘
                  │
                  ▼
6. Assemble Response → orchestrator_langgraph.py
         │
         ▼
7. Optional Email → agents/automation.py
         │              └─▶ tools/gmail_tool.py
         ▼
8. Serialize → utils.py
         │
         ▼
9. Return JSON → server.py
```

---

## 📦 Module Dependencies

### External Dependencies (requirements.txt)

```
fastapi          → server.py
uvicorn          → server.py (ASGI server)
langgraph        → orchestrator_langgraph.py
motor            → memory.py (async MongoDB)
pymongo          → memory.py
httpx            → llm_client.py (HTTP client)
pydantic         → server.py (request validation)
python-dotenv    → config.py (.env loader)
certifi          → memory.py, llm_client.py (SSL)
```

### Internal Dependencies

| File | Depends On |
|------|------------|
| `server.py` | config, orchestrator_langgraph, memory, utils |
| `orchestrator_langgraph.py` | agents/*, memory, utils, langgraph |
| `llm_client.py` | config, httpx, certifi |
| `memory.py` | motor, certifi, config (implicit) |
| `agents/base.py` | llm_client |
| `agents/*` (all agents) | base, llm_client |
| `agents/automation.py` | tools/gmail_tool, config |
| `tools/gmail_tool.py` | smtplib (stdlib) |

---

## 🔐 API Key Distribution

```
┌──────────────────────────────────────────────────┐
│           Groq API (External Service)            │
└────────┬─────────────┬────────────┬──────────────┘
         │             │            │
    Key 1 (2x)    Key 2 (2x)   Key 3 (1x)
         │             │            │
         ├─────────────┼────────────┤
         │             │            │
    ┌────▼────┐   ┌────▼────┐  ┌───▼─────┐
    │ CEO +   │   │Developer│  │ Writer  │
    │Research │   └─────────┘  └─────────┘
    └─────────┘        │
         │             │
    ┌────▼────┐   ┌────▼────┐
    │Confidence│  │Reviewer │
    └─────────┘   └─────────┘
```

**Load Balancing Strategy:**
- **Key 1** (GROQ_API_KEY): CEO+Research, Confidence (2 calls)
- **Key 2** (GROQ_API_KEY_2): Developer, Reviewer (2 calls)
- **Key 3** (GROQ_API_KEY_3): Writer (1 call)

---

## 💾 Database Connections

```
┌─────────────────────────────────────┐
│         MongoDB (External)          │
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │ sessions │  │  plans   │        │
│  └────┬─────┘  └────┬─────┘        │
│       │             │              │
│  ┌────▼─────┐  ┌────▼─────┐        │
│  │ research │  │documents │        │
│  └────┬─────┘  └────┬─────┘        │
│       │             │              │
│  ┌────▼─────────────▼─────┐        │
│  │       actions          │        │
│  └────────────────────────┘        │
└──────────────┬──────────────────────┘
               │
               ▼
         memory.py
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
orchestrator  agents/   server.py
_langgraph    confidence
```

**Collections Used:**
- **sessions**: Request metadata (`orchestrator_langgraph.py`)
- **plans**: Task breakdowns (`orchestrator_langgraph.py`)
- **research**: Research findings (`orchestrator_langgraph.py`)
- **documents**: Generated content (`orchestrator_langgraph.py`, `agents/reviewer.py`)
- **actions**: Agent actions log (`agents/confidence.py`, `agents/automation.py`)

---

## 🛠️ Tools & External Services

```
┌─────────────────────────────────┐
│     External Services           │
├─────────────────────────────────┤
│  • Groq API (LLM inference)     │
│  • MongoDB (data persistence)   │
│  • Gmail SMTP (email delivery)  │
│  • SerpAPI (unused)             │
│  • Google Calendar (unused)     │
└────────┬────────────────────────┘
         │
         ▼
    tools/ folder
         │
    ┌────┼─────────────────────┐
    │    │                     │
    ▼    ▼                     ▼
gmail_tool.py           search_tool.py
    │                   (unused)
    │
    └─▶ agents/automation.py
```

---

## 🎯 Critical Path Analysis

**Minimum Files Required to Run System:**

1. ✅ `backend/server.py` - Entry point
2. ✅ `backend/config.py` - Configuration
3. ✅ `backend/orchestrator_langgraph.py` - Orchestration
4. ✅ `backend/memory.py` - Persistence
5. ✅ `backend/llm_client.py` - LLM gateway
6. ✅ `backend/utils.py` - Utilities
7. ✅ `backend/agents/base.py` - Agent base class
8. ✅ `backend/agents/ceo.py` - Planning
9. ✅ `backend/agents/research.py` - Research
10. ✅ `backend/agents/developer.py` - Technical artifacts
11. ✅ `backend/agents/writer.py` - Document generation
12. ✅ `backend/agents/confidence.py` - Quality validation
13. ✅ `backend/agents/reviewer.py` - Issue repair ⭐
14. ✅ `backend/agents/automation.py` - Email delivery (optional)

**Optional Files:**
- `backend/tools/gmail_tool.py` - Email (if enabled)
- `backend/tools/search_tool.py` - Unused
- `backend/tools/calendar_tool.py` - Unused
- `backend/tools/file_tool.py` - Unused

---

## 📍 Configuration Flow

```
.env file
   │
   ▼
config.py (loads dotenv)
   │
   ├─▶ server.py (APP_HOST, APP_PORT)
   ├─▶ llm_client.py (GROQ_API_KEY_1/2/3)
   ├─▶ memory.py (MONGO_URI)
   ├─▶ orchestrator_langgraph.py (USE_LANGGRAPH)
   └─▶ agents/automation.py (EMAIL_ENABLED, GMAIL_*)
```

**Key Environment Variables:**
- `GROQ_API_KEY`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3` → LLM access
- `MONGO_URI` → Database connection
- `USE_LANGGRAPH` → Orchestrator selection
- `APP_HOST`, `APP_PORT` → Server binding
- `EMAIL_ENABLED`, `GMAIL_USER`, `GMAIL_APP_PASSWORD` → Email

---

## 🔍 Import Graph (Detailed)

### Circular Dependency Check: ✅ NONE

```
Level 0 (No dependencies):
  └─ config.py

Level 1 (Depends on Level 0):
  ├─ llm_client.py → config
  ├─ memory.py → config (implicit)
  └─ utils.py → (stdlib only)

Level 2 (Depends on Level 0-1):
  └─ agents/base.py → llm_client

Level 3 (Depends on Level 0-2):
  ├─ agents/ceo.py → base
  ├─ agents/research.py → base
  ├─ agents/developer.py → base
  ├─ agents/writer.py → base
  ├─ agents/confidence.py → base, memory
  ├─ agents/reviewer.py → base
  └─ agents/automation.py → base, tools/gmail_tool

Level 4 (Depends on Level 0-3):
  └─ orchestrator_langgraph.py → agents/*, memory, utils

Level 5 (Depends on Level 0-4):
  └─ server.py → config, orchestrator_langgraph, memory, utils
```

---

## 📋 Summary

### Key Relationships:

1. **server.py** is the entry point, connects to orchestrator
2. **orchestrator_langgraph.py** is the brain, coordinates all agents
3. **config.py** is the configuration hub, used by most files
4. **llm_client.py** is the LLM gateway, used by all agents
5. **memory.py** is the persistence layer, used by orchestrator and agents
6. **agents/base.py** provides common interface for all agents
7. **agents/reviewer.py** ⭐ is the new quality repair agent (Key 2)
8. **All agents** inherit from base and use llm_client

### External Dependencies:

- **Groq API** → LLM inference (5 calls per workflow)
- **MongoDB** → State persistence (sessions, plans, documents, actions)
- **Gmail SMTP** → Email delivery (optional)

### No Circular Dependencies: ✅

The architecture maintains a clean dependency hierarchy with no circular imports, ensuring maintainability and testability.

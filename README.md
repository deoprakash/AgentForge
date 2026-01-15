# AgentForge 🤖
**Enterprise-Grade Multi-Agent AI Orchestration Platform**

AgentForge is a **production-ready multi-agent AI orchestration system** that demonstrates **robust, scalable, and well-governed agent workflows** built using modern backend and AI engineering practices.

It focuses on **reliability, efficiency, and quality control** in autonomous AI systems, making it suitable for real-world deployments where correctness, cost, and scalability matter.

---

## 🚀 Problem Statement

Large Language Model (LLM) based systems often struggle in practical deployments due to:
- Uncontrolled API usage and high operational costs
- Hallucinated or unreliable outputs
- Tightly coupled or monolithic agent designs
- Single-provider dependency and rate-limit failures
- Lack of workflow governance and persistent context

### ✅ AgentForge Addresses These Challenges By:
- Introducing **governed multi-agent workflows**
- Embedding **confidence and hallucination validation**
- Optimizing LLM usage with **67% fewer API calls**
- Supporting **multi-key, rate-limit–aware execution**
- Providing a **fully asynchronous, state-driven architecture**

---

## 🧠 High-Level Workflow

```
CEO + Research
      ↓
   Developer
      ↓
     Writer
      ↓
  Confidence
      ↓
   Reviewer
      ↓
     END
```

**5 specialized agents** work together in a linear pipeline:
- Each agent has a **single, clearly defined responsibility**
- **Confidence agent** validates quality before reviewer
- **Reviewer agent** autonomously fixes detected issues
- Improves system predictability and output quality

---

## 🎯 Key System Capabilities

| Capability | Description |
|----------|-------------|
| Multi-Agent Orchestration | Modular and scalable agent workflows |
| Quality Validation | Confidence scoring and hallucination detection |
| API Call Optimization | Significant reduction in LLM usage |
| Async Architecture | High-throughput non-blocking execution |
| Persistent Memory | Context-aware task processing |
| REST API | External system integration |

---

## 🏗️ Architecture Overview

### Design Principles
- Graph-based orchestration using LangGraph
- Async-first backend using asyncio
- Stateless agents with persistent memory
- Quality gates before final output delivery
- Rate-limit-aware LLM access

### Design Patterns Used
- Factory Pattern (LLM provider abstraction)
- Strategy Pattern (API key routing)
- Repository Pattern (database access)
- State Machine Pattern (workflow orchestration)
- Separation of Concerns (agent isolation)

---

## 🧩 Core Features

### ✔ Multi-Agent Orchestration

**Agent Pipeline with API Key Distribution:**

1. **CEO + Research Agent** (API Key 1)
   - Creates strategic plan and task breakdown
   - Conducts initial research and market analysis
   - Combined into single LLM call for efficiency

2. **Developer Agent** (API Key 2)
   - Generates technical artifacts and diagrams
   - Creates Mermaid flowcharts and architecture docs
   - Produces implementation specifications

3. **Writer Agent** (API Key 3)
   - Composes final structured documents
   - Integrates research and technical content
   - Generates professional proposals and reports

4. **Confidence Agent** (API Key 1)
   - Evaluates output quality and accuracy
   - Scores confidence (0-100) and hallucination risk
   - Identifies specific issues needing correction

5. **Reviewer Agent** (API Key 2) ⭐ NEW
   - **Autonomously repairs** detected quality issues
   - Targets specific problems identified by Confidence agent
   - Preserves correct content while fixing errors
   - Adds disclaimers for unverifiable claims
   - Returns refined document as final output

### ✔ Quality Governance
- Confidence score (0–100)
- Hallucination risk classification (LOW / MEDIUM / HIGH)
- Identification of weak or uncertain sections

### ✔ Optimized LLM Usage
- Only **5 LLM calls per complete workflow**
- Multi-key load balancing (Key1: 2 calls, Key2: 2 calls, Key3: 1 call)
- Configurable execution delays (2s between nodes)
- Retry and fallback handling

### ✔ Backend Infrastructure
- FastAPI-based REST API
- Async MongoDB integration
- Environment-based configuration
- Robust error handling

---

## � Project Structure

```
AgenticAI/
├── backend/              # All Python application code
│   ├── agents/          # Agent implementations
│   │   ├── ceo.py
│   │   ├── research.py
│   │   ├── developer.py
│   │   ├── writer.py
│   │   ├── confidence.py
│   │   ├── reviewer.py  # NEW: Issue repair agent
│   │   └── automation.py
│   ├── tools/           # External integrations
│   ├── outputs/         # Generated artifacts
│   ├── config.py        # Configuration
│   ├── server.py        # FastAPI server
│   ├── orchestrator_langgraph.py  # LangGraph pipeline
│   ├── memory.py        # MongoDB persistence
│   ├── llm_client.py    # LLM API client
│   └── utils.py         # Utilities
├── docs/                # Documentation
│   ├── architecture.md
│   ├── workflows.md
│   └── file_structure.md
├── .env                 # Environment variables
└── README.md            # This file
```

---

## �🛠️ Technology Stack

| Category | Technologies |
|--------|-------------|
| Language | Python 3.12 |
| Backend | FastAPI |
| Orchestration | LangGraph |
| Async Runtime | asyncio |
| Database | MongoDB (Motor) |
| LLM Provider | Groq (multi-key routing) |
| Validation | Pydantic |
| HTTP Client | httpx |
| Config | python-dotenv |

---

## 📊 Project Metrics

![Metrics](metrics.jpeg)

- **5 specialized agents** orchestrated via LangGraph state machine
- **5 LLM calls per workflow** (optimized from 12+ autonomous calls)
- Persistent memory using MongoDB with session-based context
- Built-in confidence & hallucination risk scoring
- **Reviewer agent** for autonomous quality repair
- Optimized for cost, quality, and determinism 

---

## 🔄 Example Use Case

**Input:**  
```json
{
  "goal": "Write a proposal for warehouse automation technology"
}
```

**Workflow Execution:**

1. **CEO + Research** (2s) → Creates plan + conducts research
2. **Developer** (2s) → Generates technical diagrams
3. **Writer** (2s) → Composes full proposal document
4. **Confidence** (2s) → Evaluates quality, detects issues:
   - Confidence: 75%
   - Hallucination Risk: MEDIUM
   - Issues: ["AGV cost needs verification", "Timeline not validated"]
5. **Reviewer** (2s) → **Fixes detected issues:**
   - Adds cost range caveats
   - Marks timeline as estimate
   - Provides supporting context

**Final Output:**
```json
{
  "session_id": "ses_a3f7b2c1",
  "plan": { "tasks": [...] },
  "handoff": {
    "research": "Market analysis...",
    "developer": "```mermaid\ngraph TD...",
    "writer": "# Warehouse Automation Proposal...",
    "reviewer": "# Warehouse Automation Proposal (REVISED)..."  
  },
  "final": "# Warehouse Automation Proposal (REVISED)\n\nCost: $50K-100K (market estimates)...",
  "confidence": {
    "confidence_score": 75,
    "hallucination_risk": "medium",
    "hallucination_issues": ["AGV cost needs verification", "Timeline not validated"]
  }
}
```

**Key Features Demonstrated:**
- ✅ Autonomous issue detection by Confidence agent
- ✅ Targeted repair by Reviewer agent (no full rewrite)
- ✅ Quality improvement without human intervention
- ✅ Final output uses reviewed version

---

## ⚙️ Quick Start

### Installation
```bash
git clone https://github.com/deoprakash/AgentForge.git
cd AgentForge
pip install -r backend/requirements.txt
```

### Configuration
Create a `.env` file in the root directory:
```env
# LLM API Keys
GROQ_API_KEY=your_key_1
GROQ_API_KEY_2=your_key_2
GROQ_API_KEY_3=your_key_3

# MongoDB
MONGO_URI=mongodb+srv://...

# Orchestration
USE_LANGGRAPH=true

# Server
APP_HOST=0.0.0.0
APP_PORT=8000
```

### Run Server
```bash
cd backend
python server.py
```

API runs at:
```
http://localhost:8000
```

### Test Endpoint
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "Write a proposal for warehouse optimization"}'
```

---

## 🛣️ Future Enhancements

- Human-in-the-loop validation
- Vector database integration
- Workflow monitoring dashboard
- Docker & CI/CD pipeline
- Parallel agent execution

---

## 👨‍💻 Author

**Deo Prakash**  

GitHub: https://github.com/deoprakash  
LinkedIn: https://www.linkedin.com/in/deo-prakash-152265225/

---

## 📄 License
Apache License

---

⭐ **Star this repository if you find it useful or insightful!**

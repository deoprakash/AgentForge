# AgentForge 🤖
**Enterprise-Grade Multi-Agent AI Orchestration System with LangGraph**

A production-ready Python framework demonstrating advanced software architecture patterns for autonomous AI agent coordination, featuring LangGraph state management, async/await operations, database persistence, multi-LLM provider support, and RESTful API design.

**Technical Highlights:**
- 🏗️ **LangGraph-powered orchestration** with stateful pipeline control
- ⚡ **Asynchronous processing** using Python's asyncio and Motor
- 🔌 **Multi-key load balancing** across 3 Groq API keys with intelligent routing
- 💾 **Persistent memory layer** with MongoDB
- 🛠️ **Tool orchestration system** with Gmail, Calendar, File, and Search APIs
- 🎯 **Optimized API efficiency** - 4 calls per report (67% reduction from baseline)
- 🔍 **Built-in quality validation** with confidence scoring and hallucination detection

---

## 🎯 Engineering Problem Solved

**Challenge:** Traditional AI applications face scalability issues with monolithic architectures, lack of persistent memory, brittle single-provider dependencies, and inefficient API usage patterns.

**Solution:** Implemented a graph-based agent system using:
- **LangGraph State Management**: Explicit state transitions with conditional routing and loop control
- **Separation of Concerns**: Each agent has a single, well-defined responsibility
- **Async-first Design**: Non-blocking I/O for handling multiple concurrent requests
- **Intelligent API Key Distribution**: 3-key rotation with fixed routing per agent to optimize rate limits
- **Combined Agent Operations**: CEO+Research and Confidence+Hallucination merged into single calls
- **Stateful Memory**: MongoDB integration for conversation context and task history
- **RESTful API**: FastAPI server enabling external integrations

**Business Value:** Reduces AI integration complexity by 67% fewer API calls, improves reliability through key distribution, provides built-in quality validation, and offers a scalable foundation for enterprise automation workflows.

---

## 🔧 Core Technical Features

### Architecture & Design Patterns
- **LangGraph Orchestration** with stateful nodes and conditional edges
- **Multi-Agent Pipeline** with CEO+Research → Developer → Writer → Validation flow
- **Repository Pattern** for database abstraction
- **Factory Pattern** for LLM provider instantiation
- **Strategy Pattern** for multi-key distribution logic
- **Async/Await** throughout for optimal concurrency
- **Quality Gates** with confidence scoring and hallucination detection

### Infrastructure & DevOps
- **FastAPI + Uvicorn** for high-performance async API
- **MongoDB (Motor)** for non-blocking database operations
- **Environment-based configuration** with python-dotenv
- **Poetry/pip** for dependency management
- **Modular project structure** enabling horizontal scaling

---

## 📁 Project Architecture

```
AgenticAI/
│
├── agents/                      # Agent implementations
│   ├── ceo.py                  # Task planning & delegation
│   ├── research.py             # Information gathering
│   ├── writer.py               # Content generation
│   ├── developer.py            # Code/diagram generation
│   ├── automation.py           # Workflow execution
│   ├── reviewer.py             # Quality assurance
│   ├── confidence.py           # Output validation
│   └── base.py                 # Abstract base class
│
├── tools/                       # External integrations
│   ├── gmail_tool.py           # Email automation via Gmail API
│   ├── calendar_tool.py        # Google Calendar integration
│   ├── search_tool.py          # Web search capabilities
│   └── file_tool.py            # File system operations
│
├── orchestrator.py              # Central coordination logic
├── memory.py                    # Persistent storage layer
├── llm_client.py               # Multi-provider LLM abstraction
├── config.py                   # Environment configuration
├── server.py                   # FastAPI REST endpoints
├── utils.py                    # Helper functions
├── pyproject.toml              # Project metadata
└── requirements.txt            # Python dependencies

```

**Key Design Decisions:**
- Flat module structure for agent discovery
- Stateless agents with memory injection
- Centralized orchestrator preventing circular dependencies
- Tool encapsulation for easy testing/mocking

---

## 💻 Technology Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.12+ (async/await, type hints) |
| **Web Framework** | FastAPI 0.115.0, Uvicorn (ASGI server) |
| **Orchestration** | LangGraph 0.2.0+ (state machine framework) |
| **LLM Providers** | Groq API (3-key rotation) |
| **Database** | MongoDB (via Motor async driver) |
| **HTTP Client** | httpx (async-capable with certifi SSL) |
| **Validation** | Pydantic 2.8+ for request/response schemas |
| **Environment** | python-dotenv for configuration |
| **File I/O** | aiofiles for non-blocking operations |

---

## 📊 Project Metrics

- **Lines of Code:** ~2,500+ (Python)
- **Agents Implemented:** 6 specialized agents (CEO, Research, Developer, Writer, Automation, Confidence)
- **External Integrations:** 4 tools (Gmail, Calendar, Search, File)
- **LLM Providers Supported:** 1 primary (Groq with 3-key rotation)
- **API Calls per Report:** 4 (CEO+Research: 1, Developer: 1, Writer: 1, Validation: 1)
- **API Efficiency Gain:** 67% reduction from baseline (was 12 calls with retries)
- **Async Operations:** 100% async-first design
- **Database Operations:** Fully async with Motor driver
- **State Transitions:** 2-second delays between pipeline stages

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+ (uses modern async features)
- MongoDB instance (local or Atlas)
- API keys for at least one LLM provider

### 1. Clone Repository
```bash
git clone https://github.com/deoprakash/AgentForge.git
cd AgentForge
```

### 2. Create Virtual Environment
```bash
# Recommended: Use Python virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Server Configuration
APP_HOST=0.0.0.0
APP_PORT=8000

# LangGraph Orchestration (toggle graph-based pipeline)
USE_LANGGRAPH=true

# LLM Provider Selection (groq recommended)
LLM_PROVIDER=groq
LLM_GENERATION_PROVIDER=groq      # Optional: override for generation tasks
LLM_VALIDATION_PROVIDER=groq      # Optional: override for validation

# Groq API Configuration (3-key rotation for optimal throughput)
GROQ_API_KEY=gsk_...              # Key 1: CEO+Research, Validation
GROQ_API_KEY_2=gsk_...            # Key 2: Developer
GROQ_API_KEY_3=gsk_...            # Key 3: Writer
GROQ_KEY_STRATEGY=rotation        # Strategy: single | rotation | failover_on_429
GROQ_MIN_INTERVAL_SECONDS=0.4     # Rate limiting spacing
GROQ_VALIDATION_MODEL=llama-3.1-8b-instant

# Database
MONGO_URI=mongodb://localhost:27017/AgentForge
# Or MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/

# Email Integration (optional)
EMAIL_ENABLED=false
ALLOW_EMAIL_SENDING=false
ADMIN_EMAIL=admin@example.com
FROM_EMAIL=no-reply@example.com
```

**Security Note:** Never commit `.env` to version control. Add it to `.gitignore`.

---

## 🏃 Running the Application

### Start the API Server
```bash
python server.py
```

The FastAPI server will start on `http://localhost:8000`

**API Endpoints:**
- `POST /run` - Execute agent workflow with goal and email
- `POST /run/legacy` - Legacy endpoint for backward compatibility

### Example API Request
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Research latest AI agent frameworks and email results to user@example.com"
  }'
```

Or using the structured format:
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Research latest AI agent frameworks",
    "email": "user@example.com"
  }'
```

---

## 🔄 System Workflow

**Example Task:** *"Write a proposal for supply chain technology"*

### Execution Flow with LangGraph:

1. **API Layer** (`server.py`)
   - Receives HTTP POST request
   - Validates input via Pydantic models
   - Selects LangGraph orchestrator (via `USE_LANGGRAPH=true`)

2. **LangGraph State Machine** (`orchestrator_langgraph.py`)
   - Creates session in memory store
   - Initializes pipeline state with goal and session ID

3. **Node 1: CEO + Research** (API Key 1)
   - Creates strategic plan with Developer and Writer tasks
   - Performs initial research in same LLM call
   - Saves plan and research to MongoDB
   - **API Calls: 1**

4. **Node 2: Developer** (API Key 2, 2s delay)
   - Uses research context to generate technical artifacts
   - Creates mermaid diagrams or architecture outlines
   - **API Calls: 1**

5. **Node 3: Writer** (API Key 3, 2s delay)
   - Retrieves research and developer outputs from state
   - Generates formatted final document
   - Persists output to database
   - **API Calls: 1**

6. **Node 4: Validation** (API Key 1, 2s delay)
   - Evaluates confidence score (0-100)
   - Detects hallucination risk (LOW/MEDIUM/HIGH)
   - Identifies specific issues if any
   - Saves quality report to MongoDB
   - **API Calls: 1**

7. **Output & Metrics**
   - Prints confidence and hallucination scores to console
   - Optionally sends formatted email via Gmail tool
   - Returns JSON with session, plan, handoff, final document, and confidence

**Total API Calls: 4 per report**

**Result:** Structured JSON response with:
- Plan breakdown by agent
- Research findings
- Technical artifacts (diagrams, architecture)
- Final document
- Quality metrics (confidence + hallucination)
- Email delivery status (if enabled)

---

## 🎓 Technical Skills Demonstrated

This project showcases proficiency in:

### Backend Development
- ✅ **Asynchronous Python**: Extensive use of `async/await`, `asyncio`
- ✅ **RESTful API Design**: FastAPI with Pydantic validation
- ✅ **Database Design**: MongoDB schema design and async queries
- ✅ **Design Patterns**: Factory, Strategy, Repository, State Machine
- ✅ **LangGraph**: Stateful orchestration with conditional routing

### AI/ML Engineering
- ✅ **LLM Integration**: Multi-key rotation with intelligent routing
- ✅ **Prompt Engineering**: Structured prompts with JSON output parsing
- ✅ **Agent Architectures**: Graph-based pipeline with quality gates
- ✅ **Error Handling**: Retry logic, failover strategies, graceful degradation
- ✅ **Quality Assurance**: Confidence scoring and hallucination detection

### Software Engineering
- ✅ **Modular Architecture**: Clear separation of concerns
- ✅ **Configuration Management**: Environment-based config with validation
- ✅ **Error Handling**: Comprehensive exception handling and logging
- ✅ **Type Safety**: Extensive use of type hints and Pydantic models
- ✅ **Code Organization**: DRY principles, reusable utilities
- ✅ **Performance Optimization**: 67% API call reduction through agent combination

### DevOps & Integration
- ✅ **External APIs**: Gmail, Google Calendar, Search integration
- ✅ **Environment Management**: Docker-ready, env-based configuration
- ✅ **Dependency Management**: Poetry/pip with pinned versions
- ✅ **Production Readiness**: Rate limiting, key rotation, connection pooling
- ✅ **Windows Compatibility**: Event loop policy and SSL certificate handling

---

## 🔌 Extension Points

The framework is designed for extensibility:

### Adding New Agents
```python
# agents/your_agent.py
from agents.base import BaseAgent

class YourAgent(BaseAgent):
    async def execute_task(self, task: str):
        # Your implementation
        pass
```

### Creating Custom Tools
```python
# tools/your_tool.py
async def your_tool_function(params):
    # Tool implementation
    return result
```

### Adding LLM Providers
Extend `llm_client.py` with new provider implementations following the existing pattern.

---

## 🛣️ Future Enhancements

- [ ] Vector database integration (Pinecone/Weaviate) for semantic memory
- [ ] React-based admin dashboard with real-time LangGraph visualization
- [ ] Docker containerization with docker-compose
- [ ] Comprehensive test suite (pytest + pytest-asyncio)
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Human-in-the-loop approval workflow for quality gates
- [ ] Parallel node execution for independent operations
- [ ] Custom confidence threshold configuration per use case

---

## 🤝 Contributing

Contributions are welcome! This project follows standard open-source practices:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Code Standards:**
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public APIs
- Maintain async consistency

---

## 👨‍💻 Author

**Deo Prakash**  
*Full-Stack Developer | AI/ML Engineer*

- 🔗 GitHub: [@deoprakash](https://github.com/deoprakash)
- 💼 LinkedIn: [Deo Prakash](https://www.linkedin.com/in/deo-prakash-152265225/)
- 📧 Contact: Available via LinkedIn

**Technical Expertise:**
- Backend: Python, FastAPI, Node.js
- AI/ML: LLM Integration, Agent Systems, Prompt Engineering
- Databases: MongoDB, PostgreSQL, Redis
- DevOps: Docker, CI/CD, Cloud Deployment

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- FastAPI team for the excellent async framework
- Anthropic, Google, and Groq for LLM API access
- MongoDB team for Motor async driver
- Open-source AI community for inspiration

---

**⭐ Star this repository if you find it useful for learning or reference!**

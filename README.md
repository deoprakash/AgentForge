# AgentForge 🤖
**Enterprise-Grade Multi-Agent AI Orchestration System**

A production-ready Python framework demonstrating advanced software architecture patterns for autonomous AI agent coordination, featuring async/await operations, database persistence, multi-LLM provider support, and RESTful API design.

**Technical Highlights:**
- 🏗️ **Microservices-style agent architecture** with 7 specialized agents
- ⚡ **Asynchronous processing** using Python's asyncio and Motor
- 🔌 **Multi-provider LLM integration** (Groq, Google Gemini, Ollama)
- 💾 **Persistent memory layer** with MongoDB
- 🛠️ **Tool orchestration system** with Gmail, Calendar, File, and Search APIs
- 🔄 **Failover & retry logic** for production reliability

---

## 🎯 Engineering Problem Solved

**Challenge:** Traditional AI applications face scalability issues with monolithic architectures, lack of persistent memory, and brittle single-provider dependencies.

**Solution:** Implemented a distributed agent system using:
- **Separation of Concerns**: Each agent has a single, well-defined responsibility
- **Async-first Design**: Non-blocking I/O for handling multiple concurrent requests
- **Provider Abstraction**: Unified LLM client supporting multiple backends with automatic failover
- **Stateful Memory**: MongoDB integration for conversation context and task history
- **RESTful API**: FastAPI server enabling external integrations

**Business Value:** Reduces AI integration complexity, improves reliability through redundancy, and provides a scalable foundation for enterprise automation workflows.

---

## 🔧 Core Technical Features

### Architecture & Design Patterns
- **Multi-Agent Orchestration** with CEO-driven task delegation
- **Repository Pattern** for database abstraction
- **Factory Pattern** for LLM provider instantiation
- **Strategy Pattern** for multi-key failover logic
- **Async/Await** throughout for optimal concurrency

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
| **Language** | Python 3.10+ (async/await, type hints) |
| **Web Framework** | FastAPI 0.115.0, Uvicorn (ASGI server) |
| **LLM Providers** | Groq API, Google Gemini AI, Ollama (local) |
| **Database** | MongoDB (via Motor async driver) |
| **HTTP Client** | httpx (async-capable) |
| **Validation** | Pydantic 2.8+ for request/response schemas |
| **Environment** | python-dotenv for configuration |
| **File I/O** | aiofiles for non-blocking operations |

---

## 📊 Project Metrics

- **Lines of Code:** ~2,000+ (Python)
- **Agents Implemented:** 7 specialized agents
- **External Integrations:** 4 tools (Gmail, Calendar, Search, File)
- **LLM Providers Supported:** 3 (Groq, Gemini, Ollama)
- **Async Operations:** 100% async-first design
- **Database Operations:** Fully async with Motor driver

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

# LLM Provider Selection (groq | gemini | ollama)
LLM_PROVIDER=groq
LLM_GENERATION_PROVIDER=groq      # Optional: override for generation tasks
LLM_VALIDATION_PROVIDER=gemini    # Optional: override for validation

# Groq API Configuration
GROQ_API_KEY=gsk_...
GROQ_API_KEY_2=gsk_...            # Optional: failover key
GROQ_API_KEYS=key1,key2,key3      # Optional: comma-separated for rotation
GROQ_KEY_STRATEGY=failover_on_429 # Strategy: single | failover_on_429
GROQ_MIN_INTERVAL_SECONDS=1.5     # Rate limiting spacing

# Google Gemini Configuration
GEMINI_API_KEY=AIza...
GEMINI_API_KEY_2=AIza...          # Optional: failover key
GEMINI_API_KEYS=key1,key2         # Optional: comma-separated

# Ollama Configuration (for local deployment)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Database
MONGO_URI=mongodb://localhost:27017/AgentForge
# Or MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/

# Email Integration
EMAIL_ENABLED=true
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

**Example Task:** *"Research autonomous AI agents and create a technical report"*

### Execution Flow:

1. **API Layer** (`server.py`)
   - Receives HTTP POST request
   - Validates input via Pydantic models
   - Initiates orchestrator

2. **Orchestrator** (`orchestrator.py`)
   - Creates session in memory store
   - Delegates to CEO agent for planning

3. **CEO Agent** (`agents/ceo.py`)
   - Analyzes goal and creates structured task plan
   - Assigns tasks to specialized agents (Research → Writer → Reviewer)

4. **Research Agent** (`agents/research.py`)
   - Uses `search_tool.py` to gather information
   - Saves findings to MongoDB via memory layer

5. **Writer Agent** (`agents/writer.py`)
   - Retrieves research from memory
   - Generates formatted document
   - Persists output to database

6. **Automation Agent** (`agents/automation.py`)
   - Uses `gmail_tool.py` to send results
   - Optionally schedules follow-ups via `calendar_tool.py`

7. **Memory Layer** (`memory.py`)
   - Stores session context, plans, research, documents
   - Enables retrieval for multi-turn interactions

**Result:** Structured JSON response with document content and execution metadata

---

## 🎓 Technical Skills Demonstrated

This project showcases proficiency in:

### Backend Development
- ✅ **Asynchronous Python**: Extensive use of `async/await`, `asyncio`
- ✅ **RESTful API Design**: FastAPI with Pydantic validation
- ✅ **Database Design**: MongoDB schema design and async queries
- ✅ **Design Patterns**: Factory, Strategy, Repository, Base Class abstraction

### AI/ML Engineering
- ✅ **LLM Integration**: Multi-provider support (Groq, Gemini, Ollama)
- ✅ **Prompt Engineering**: Structured prompts with JSON output parsing
- ✅ **Agent Architectures**: CEO-worker pattern for task delegation
- ✅ **Error Handling**: Retry logic, failover strategies, graceful degradation

### Software Engineering
- ✅ **Modular Architecture**: Clear separation of concerns
- ✅ **Configuration Management**: Environment-based config with validation
- ✅ **Error Handling**: Comprehensive exception handling and logging
- ✅ **Type Safety**: Extensive use of type hints and Pydantic models
- ✅ **Code Organization**: DRY principles, reusable utilities

### DevOps & Integration
- ✅ **External APIs**: Gmail, Google Calendar, Search integration
- ✅ **Environment Management**: Docker-ready, env-based configuration
- ✅ **Dependency Management**: Poetry/pip with pinned versions
- ✅ **Production Readiness**: Rate limiting, failover, connection pooling

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
- [ ] React-based admin dashboard with real-time monitoring
- [ ] Docker containerization with docker-compose
- [ ] Comprehensive test suite (pytest + pytest-asyncio)
- [ ] CI/CD pipeline with GitHub Actions

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

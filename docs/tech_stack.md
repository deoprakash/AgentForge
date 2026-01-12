# Technology Stack

## Overview

AgentForge leverages a modern Python async stack optimized for LLM orchestration, stateful workflows, and low-latency API interactions.

---

## Core Dependencies

### Python Runtime
- **Version**: 3.12+
- **Why**: Native type hints, async/await improvements, performance optimizations
- **Key Features Used**:
  - Type hints with `TypedDict`
  - `asyncio` for concurrent operations
  - F-strings for string formatting

---

## Web Framework

### FastAPI 0.115.0
- **Purpose**: REST API server
- **Why Chosen**:
  - Native async support (ASGI)
  - Automatic OpenAPI schema generation
  - Pydantic integration for validation
  - High performance (Starlette-based)
- **Key Features Used**:
  - `@app.post("/run")` endpoint decorator
  - `BaseModel` request validation
  - `JSONResponse` for serialization
- **Documentation**: https://fastapi.tiangolo.com/

### Uvicorn 0.31.0
- **Purpose**: ASGI server for FastAPI
- **Why Chosen**:
  - Lightning-fast async server
  - Auto-reload during development
  - Production-ready with gunicorn
- **Configuration**:
  - Host: `0.0.0.0` (all interfaces)
  - Port: `8000` (default)
  - Reload: Disabled on Windows (stdin compatibility)
- **Documentation**: https://www.uvicorn.org/

---

## LLM Orchestration

### LangGraph 0.2.48
- **Purpose**: Graph-based workflow orchestration
- **Why Chosen**:
  - Stateful agent pipelines
  - Conditional routing support
  - Built-in checkpointing
  - LangChain ecosystem integration
- **Key Features Used**:
  - `StateGraph` for pipeline definition
  - `TypedDict` state typing
  - Node-based execution model
  - Edge transitions with delays
- **Alternative Considered**: CrewAI (less flexible state management)
- **Documentation**: https://langchain-ai.github.io/langgraph/

### LangChain Core 0.3.15
- **Purpose**: LLM abstraction framework (dependency of LangGraph)
- **Usage**: Not directly used; LangGraph inherits utilities
- **Documentation**: https://python.langchain.com/

---

## HTTP Client

### httpx 0.27.0
- **Purpose**: Async HTTP client for LLM API calls
- **Why Chosen**:
  - Native async/await support
  - HTTP/2 support
  - Superior to `requests` (sync) and `aiohttp` (less intuitive API)
- **Key Features Used**:
  - `AsyncClient` context manager
  - Custom SSL verification with certifi
  - Timeout configuration (30s)
- **Example**:
  ```python
  async with httpx.AsyncClient(timeout=30, verify=certifi.where()) as client:
      response = await client.post(url, headers=headers, json=body)
  ```
- **Documentation**: https://www.python-httpx.org/

### certifi 2024.8.30
- **Purpose**: Mozilla CA bundle for SSL verification
- **Why Needed**: Fixes "self-signed certificate in chain" errors
- **Usage**:
  ```python
  import certifi
  httpx.AsyncClient(verify=certifi.where())
  ```
- **Alternative**: System CA bundle (unreliable on Windows)
- **Documentation**: https://github.com/certifi/python-certifi

---

## Database

### Motor 3.5.1
- **Purpose**: Async MongoDB driver
- **Why Chosen**:
  - Official MongoDB async driver for Python
  - asyncio-native (no threading)
  - Compatible with PyMongo API
- **Key Features Used**:
  - `AsyncIOMotorClient` connection
  - TLS configuration with certifi
  - CRUD operations on collections
- **Example**:
  ```python
  client = AsyncIOMotorClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
  db = client["AgentForge"]
  await db.sessions.insert_one(document)
  ```
- **Alternative Considered**: PostgreSQL (less flexible schema for agent outputs)
- **Documentation**: https://motor.readthedocs.io/

### PyMongo 4.8.0
- **Purpose**: Synchronous MongoDB driver (Motor dependency)
- **Usage**: Type hints and helpers used by Motor
- **Documentation**: https://pymongo.readthedocs.io/

---

## Validation & Data Modeling

### Pydantic 2.8.2
- **Purpose**: Data validation and settings management
- **Why Chosen**:
  - FastAPI native integration
  - Type-safe models
  - Automatic JSON schema generation
- **Key Features Used**:
  - `BaseModel` for request validation
  - Type hints for field validation
  - `model_validate()` for dict parsing
- **Example**:
  ```python
  class RunRequest(BaseModel):
      command: str  # Required string field
  ```
- **Documentation**: https://docs.pydantic.dev/

---

## Configuration Management

### python-dotenv 1.0.1
- **Purpose**: Load environment variables from `.env` file
- **Why Chosen**:
  - Industry-standard for config management
  - No external dependencies
  - Simple API
- **Usage**:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  os.getenv("GROQ_API_KEY")
  ```
- **Alternative**: Direct environment variables (less convenient for dev)
- **Documentation**: https://github.com/theskumar/python-dotenv

---

## LLM Provider

### Groq API
- **Model**: `llama-3.1-8b-instant`
- **Why Chosen**:
  - Fastest inference in market (LPU architecture)
  - Free tier: 30 requests/min per key (90 RPM with 3 keys)
  - Low latency (~1-2s response time)
- **API Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Rate Limits**:
  - 30 requests/min per key
  - 14400 tokens/min per model
- **Alternative Considered**: OpenAI GPT-4 (expensive), Anthropic Claude (slower)
- **Documentation**: https://console.groq.com/docs

---

## Dependency Management

### Poetry 1.8.0
- **Purpose**: Python dependency and packaging management
- **Why Chosen**:
  - Deterministic dependency resolution
  - Virtual environment management
  - `pyproject.toml` standard compliance
- **Commands**:
  ```bash
  poetry install               # Install deps
  poetry add <package>         # Add dependency
  poetry export > requirements.txt  # Generate pip format
  ```
- **Alternative**: pip + requirements.txt (less reliable locking)
- **Documentation**: https://python-poetry.org/

---

## Complete Dependency List

### Production Dependencies (`pyproject.toml`)
```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = "^0.31.0"
langgraph = "^0.2.0"
langchain-core = "^0.3.15"
httpx = "^0.27.0"
motor = "^3.5.1"         # Async MongoDB
pymongo = "^4.8.0"       # Motor dependency
certifi = "^2024.8.30"   # SSL certificates
pydantic = "^2.8.2"
python-dotenv = "^1.0.1"
```

### Development Dependencies
```toml
[tool.poetry.dev-dependencies]
pytest = "^8.0.0"         # Testing framework (not yet used)
black = "^24.0.0"         # Code formatter (not yet used)
mypy = "^1.10.0"          # Type checker (not yet used)
```

---

## External Services

### MongoDB Atlas
- **Purpose**: Cloud-hosted MongoDB database
- **Plan**: Free tier (M0 Sandbox)
- **Features**:
  - 512 MB storage
  - Auto-scaling
  - Built-in backups
  - TLS encryption
- **Connection**: `mongodb+srv://` URI with Motor
- **Alternative**: Self-hosted MongoDB (more maintenance)
- **Documentation**: https://www.mongodb.com/atlas

### Gmail SMTP
- **Purpose**: Email delivery
- **Server**: `smtp.gmail.com:587` (TLS)
- **Authentication**: App-specific password (2FA required)
- **Rate Limits**: 500 emails/day (free tier)
- **Alternative Considered**: SendGrid, AWS SES (overkill for current usage)
- **Documentation**: https://support.google.com/mail/answer/7126229

---

## Development Tools

### VS Code Extensions (Recommended)
- **Python**: Microsoft Python extension
- **Pylance**: Fast language server
- **Jupyter**: Notebook support for testing
- **REST Client**: Test FastAPI endpoints
- **Mermaid Preview**: View generated diagrams

---

## Performance Characteristics

### Latency Breakdown (Typical Request)
| Component | Latency |
|-----------|---------|
| FastAPI routing | ~5ms |
| MongoDB write | ~50-100ms |
| LLM API call (CEO+Research) | ~8-12s |
| LLM API call (Developer) | ~5-8s |
| LLM API call (Writer) | ~10-15s |
| LLM API call (Validation) | ~3-5s |
| Gmail SMTP send | ~1-2s |
| **Total** | **~33-48s** |

### Throughput Limits
- **LLM API**: 30 requests/min per key → 90 RPM total
- **MongoDB**: 100+ concurrent connections (M0 tier)
- **FastAPI**: 1000+ requests/sec (CPU-bound)
- **Bottleneck**: LLM API rate limits

### Memory Usage
- **Baseline**: ~50 MB (Python runtime)
- **Per Request**: ~5-10 MB (state + LLM responses)
- **Peak**: ~150 MB (10 concurrent requests)

---

## Security Stack

### SSL/TLS
- **HTTP Client**: certifi CA bundle
- **MongoDB**: TLS 1.2+ with certificate verification
- **Email**: STARTTLS (port 587)

### Secrets Management
- **Method**: Environment variables via `.env`
- **Git**: `.env` in `.gitignore`
- **Best Practice**: Never commit API keys

### Input Validation
- **Framework**: Pydantic + FastAPI
- **Injection Protection**: No SQL (MongoDB uses BSON)
- **Rate Limiting**: Enforced at LLM API level

---

## Platform Compatibility

### Operating Systems
- **Linux**: Full support (primary development)
- **macOS**: Full support
- **Windows**: Special handling required:
  - `WindowsSelectorEventLoopPolicy` for asyncio
  - Uvicorn reload disabled (stdin issues)

### Python Versions
- **Minimum**: 3.12
- **Tested**: 3.12.0
- **Recommended**: 3.12.x (latest patch)

---

## Technology Decision Rationale

### Why Async Stack?
- LLM API calls are I/O-bound (10-15s per call)
- Async allows concurrent request handling
- MongoDB Motor is async-native
- FastAPI provides async routing

### Why LangGraph over CrewAI?
| Feature | LangGraph | CrewAI |
|---------|-----------|--------|
| State management | Explicit `TypedDict` | Implicit crew state |
| Conditional routing | Native | Limited |
| Checkpointing | Built-in | Manual |
| Flexibility | High (custom nodes) | Medium (predefined roles) |

### Why MongoDB over PostgreSQL?
- Schema flexibility (agent outputs vary)
- Native JSON support (no ORM needed)
- Async driver (Motor)
- Free hosted tier (Atlas)

---

## Versioning Strategy

### Dependency Pinning
- **Exact versions** in `poetry.lock`
- **Caret ranges** in `pyproject.toml` (e.g., `^0.2.0`)
- **Reason**: Balance stability + security updates

### Upgrade Policy
- **LangGraph**: Pin to `0.2.x` (breaking changes in 0.3+)
- **FastAPI**: Allow minor updates (`^0.115.0`)
- **httpx**: Lock to `0.27.x` (API stable)

---

## Monitoring & Observability (Future)

### Recommended Additions
- **APM**: Datadog, New Relic
- **Logging**: loguru for structured logs
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry

---

## Known Limitations

### LangGraph
- No built-in parallel execution (sequential nodes only)
- State size limit: ~1 MB per execution

### Groq API
- 30 RPM per key (mitigated with 3 keys)
- Context window: 8192 tokens (llama-3.1-8b-instant)
- No streaming support in current implementation

### MongoDB Atlas (Free Tier)
- 512 MB storage limit
- No automated backups
- Single region deployment

---

## Future Stack Enhancements

### Short Term
1. **Redis**: Cache frequent LLM responses
2. **Celery**: Background task queue for email
3. **Prometheus**: Export metrics

### Long Term
1. **Kubernetes**: Container orchestration
2. **RabbitMQ**: Message broker for async jobs
3. **PostgreSQL**: Add RDBMS for structured data
4. **OpenTelemetry**: Distributed tracing

---

## References

- [Architecture Documentation](architecture.md)
- [File Structure](file_structure.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Official Python Docs](https://docs.python.org/3.12/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [LangGraph Concepts](https://langchain-ai.github.io/langgraph/concepts/)

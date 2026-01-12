# Troubleshooting Guide

## Common Issues and Solutions

This document covers errors encountered during development, their root causes, and proven solutions.

---

## SSL Certificate Errors

### Error Message
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

### Context
- Occurred when making HTTPS requests to Groq API via `httpx`
- More common on Windows due to system CA bundle issues
- Also affects MongoDB Atlas TLS connections

### Root Cause
Python's `ssl` module couldn't locate system CA certificates, causing all HTTPS requests to fail verification.

### Solution
Install and use `certifi` package for Mozilla's trusted CA bundle:

**1. Add certifi dependency:**
```bash
poetry add certifi
```

**2. Update HTTP client (llm_client.py):**
```python
import certifi
import httpx

async with httpx.AsyncClient(timeout=30, verify=certifi.where()) as client:
    response = await client.post(url, headers=headers, json=body)
```

**3. Update MongoDB client (memory.py):**
```python
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    mongo_uri,
    tls=True,
    tlsCAFile=certifi.where()  # Use certifi CA bundle
)
```

### Prevention
- Always use `certifi.where()` for SSL verification in production
- Alternative: Disable verification with `verify=False` (NOT RECOMMENDED for production)

---

## Windows Multiprocessing Errors

### Error Message 1: LangGraph Node Registration
```
ValueError: Found edge starting at unknown node 'writer'
```

### Context
- Occurred during LangGraph graph compilation on Windows
- Related to function definition order and multiprocessing pickle behavior

### Root Cause
LangGraph nodes were referenced in edges before being registered in the graph. Windows' multiprocessing uses pickle serialization which is stricter about object references.

### Solution
Register all nodes BEFORE adding edges:

```python
# ✅ CORRECT ORDER
graph = StateGraph(PipelineState)

# 1. Register all nodes first
graph.add_node("ceo_and_research", self.node_ceo_and_research)
graph.add_node("developer", self.node_developer)
graph.add_node("writer", self.node_writer)
graph.add_node("validation", self.node_validation)

# 2. Then add edges
graph.set_entry_point("ceo_and_research")
graph.add_edge("ceo_and_research", "developer")
graph.add_edge("developer", "writer")
graph.add_edge("writer", "validation")
graph.add_edge("validation", END)

# 3. Finally compile
self.runnable = graph.compile()
```

### Prevention
- Always register nodes before wiring edges
- Test graph compilation before adding complex logic

---

### Error Message 2: Uvicorn Reload on Windows
```
ValueError: I/O operation on closed file
subprocess.CalledProcessError: Command '...' died with <Signals.SIGTERM: 15>
```

### Context
- Occurs when running FastAPI with Uvicorn's auto-reload feature on Windows
- Related to stdin/stdout handling in subprocesses

### Root Cause
Uvicorn's reload mechanism spawns subprocesses that inherit closed stdin/stdout handles on Windows.

### Solution
Disable auto-reload on Windows and set proper event loop policy:

**Update server.py:**
```python
import asyncio
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    # Fix asyncio event loop for Windows
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Disable reload on Windows to prevent stdin errors
    uvicorn.run(
        app,
        host=APP_HOST,
        port=APP_PORT,
        reload=False  # Set to True only on Linux/macOS
    )
```

**Alternative** (for development):
```python
# Use conditional reload
reload_enabled = os.name != 'nt'  # False on Windows, True elsewhere
uvicorn.run(app, reload=reload_enabled)
```

### Prevention
- Use `asyncio.WindowsSelectorEventLoopPolicy()` on Windows
- Consider Docker for consistent dev environment

---

## MongoDB Connection Errors

### Error Message
```
pymongo.errors.ServerSelectionTimeoutError: <mongo-uri>:27017: [SSL: CERTIFICATE_VERIFY_FAILED]
```

### Context
- MongoDB Atlas uses TLS/SSL for all connections
- Same root cause as Groq API SSL error

### Solution
Add `tlsCAFile` parameter with certifi:

```python
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

client = AsyncIOMotorClient(
    mongo_uri,
    tls=True,
    tlsCAFile=certifi.where()
)
```

### Prevention
- Always enable TLS for MongoDB Atlas
- Test connection with `await client.admin.command('ping')`

---

## LLM API Rate Limiting

### Error Message
```
429 Client Error: Too Many Requests
```

### Context
- Groq API free tier: 30 requests/min per key
- Occurs when making rapid sequential calls

### Root Cause
Exceeded rate limit of 30 RPM per API key.

### Solution 1: Multi-Key Rotation
```python
# config.py
GROQ_API_KEY=gsk_...
GROQ_API_KEY_2=gsk_...
GROQ_API_KEY_3=gsk_...
GROQ_KEY_STRATEGY=rotation
```

**Effect**: 30 RPM × 3 keys = 90 RPM total capacity

### Solution 2: Global Pacing
```python
# config.py
GROQ_MIN_INTERVAL_SECONDS=0.4  # 0.4s = 150 req/min max (well under limit)

# llm_client.py
last_call = _last_call_times.get(api_key, 0)
elapsed = time.time() - last_call
if elapsed < GROQ_MIN_INTERVAL_SECONDS:
    await asyncio.sleep(GROQ_MIN_INTERVAL_SECONDS - elapsed)
```

### Solution 3: State Transition Delays
```python
# orchestrator_langgraph.py
async def node_developer(state):
    await asyncio.sleep(2)  # 2-second delay before execution
    result = await self.developer.execute(...)
    return {"developer": result}
```

### Prevention
- Use fixed key routing to distribute load
- Add exponential backoff for retries
- Monitor rate limit headers in API responses

---

## JSON Parsing Errors

### Error Message
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

### Context
- LLM responses sometimes include markdown code fences or explanations
- Example bad response:
  ```
  Here's the JSON:
  ```json
  {"plan": [...]}
  ```
  ```

### Root Cause
LLM added formatting that isn't valid JSON.

### Solution 1: Prompt Engineering
```python
prompt = f"""
Return ONLY valid JSON with no markdown or explanations.

Expected format:
{{"plan": [...], "research": "..."}}

Goal: {goal}
"""
```

### Solution 2: Response Cleaning
```python
import re
import json

def clean_json_response(text: str) -> str:
    # Remove markdown code fences
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Extract first JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

# Usage
response = await llm_call(...)
cleaned = clean_json_response(response)
data = json.loads(cleaned)
```

### Prevention
- Use structured output mode if available (Groq roadmap)
- Add retry logic with clearer prompts
- Validate schema with Pydantic

---

## Memory/State Persistence Issues

### Error Message
```
KeyError: 'research'
```

### Context
- Occurs when accessing state that hasn't been populated
- Common in LangGraph nodes that depend on previous outputs

### Root Cause
Node tried to access state field before it was set.

### Solution: Type-Safe State Access
```python
from typing import TypedDict

class PipelineState(TypedDict):
    session_id: str
    goal: str
    plan: List[Dict] | None  # Explicit None default
    research: str | None
    developer: str | None
    writer: str | None
    confidence: Dict | None

async def node_writer(state: PipelineState):
    # Safe access with get()
    research = state.get("research", "No research available")
    developer = state.get("developer", "")
    
    # Or explicit check
    if not state.get("research"):
        return {"writer": "ERROR: Missing research data"}
```

### Prevention
- Use `TypedDict` for explicit state schema
- Access state with `.get()` for optional fields
- Add validation at node entry points

---

## Email Delivery Failures

### Error Message
```
smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

### Context
- Gmail requires App Password (not account password) when 2FA enabled

### Solution
**1. Enable 2-Factor Authentication on Gmail**

**2. Generate App Password:**
- Go to: https://myaccount.google.com/apppasswords
- Select "Mail" and device
- Copy 16-character password (format: `xxxx xxxx xxxx xxxx`)

**3. Update .env:**
```env
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  # With spaces or without
```

**4. Verify flags:**
```env
EMAIL_ENABLED=true
ALLOW_EMAIL_SENDING=true
```

### Prevention
- Never use account password for SMTP
- Store App Password securely (environment variable)

---

## Import Errors

### Error Message
```
ModuleNotFoundError: No module named 'agents'
```

### Context
- Python can't find local modules
- Common when running scripts from wrong directory

### Solution
**1. Run from project root:**
```bash
cd c:\Users\deopr\.vscode\Projects\AgenticAI
python server.py
```

**2. Or add project to PYTHONPATH:**
```bash
# Windows PowerShell
$env:PYTHONPATH="c:\Users\deopr\.vscode\Projects\AgenticAI"
python server.py

# Linux/macOS
export PYTHONPATH=/path/to/AgenticAI
python server.py
```

**3. Use absolute imports:**
```python
# ✅ CORRECT
from agents.ceo import CEOAgent
from config import GROQ_API_KEY

# ❌ WRONG (only works in same directory)
from ceo import CEOAgent
```

### Prevention
- Always run from project root
- Use absolute imports in all files

---

## LangGraph Compilation Errors

### Error Message
```
langgraph.errors.InvalidUpdateError: State field 'research' not in schema
```

### Context
- Returned state update doesn't match `TypedDict` schema

### Solution
Ensure all node returns match state schema:

```python
class PipelineState(TypedDict):
    session_id: str
    goal: str
    research: str | None  # Must match return type

async def node_ceo_and_research(state: PipelineState) -> PipelineState:
    # ✅ CORRECT: Returns dict matching schema
    return {
        "research": "Research findings...",
        "plan": [...]
    }
    
    # ❌ WRONG: Typo in key name
    return {"researchData": "..."}  # KeyError!
```

### Prevention
- Use `TypedDict` for compile-time checks
- Enable mypy type checking
- Test graph compilation in unit tests

---

## Performance Issues

### Symptom: Slow Response Times (>60s)

### Causes & Solutions

**1. Too Many Sequential LLM Calls**
```python
# ❌ SLOW: 6 sequential calls
plan = await ceo.create_plan()        # ~8s
research = await ceo.do_research()    # ~10s
dev = await developer.execute()       # ~6s
writer = await writer.execute()       # ~12s
confidence = await confidence.score() # ~4s
hallucination = await confidence.check() # ~4s
# Total: ~44s

# ✅ FAST: 4 calls with combined operations
plan, research = await ceo.create_plan_and_research()  # ~10s
dev = await developer.execute()       # ~6s
writer = await writer.execute()       # ~12s
confidence = await confidence.evaluate_and_store()  # ~5s (combined)
# Total: ~33s (25% faster)
```

**2. No Rate Limiting Protection**
- Add `GROQ_MIN_INTERVAL_SECONDS=0.4`
- Use multi-key rotation

**3. Blocking Database Operations**
```python
# ❌ SLOW: Sync driver
import pymongo
client = pymongo.MongoClient(uri)
db.collection.insert_one(doc)  # Blocks async event loop

# ✅ FAST: Async driver
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(uri)
await db.collection.insert_one(doc)  # Non-blocking
```

### Prevention
- Combine related LLM calls where possible
- Use async drivers for all I/O
- Profile with `time.time()` checkpoints

---

## Environment Variable Issues

### Error Message
```
KeyError: 'GROQ_API_KEY'
```

### Context
- Environment variable not loaded or misspelled

### Solution
**1. Verify .env file exists:**
```bash
ls -la | grep .env  # Linux/macOS
dir | findstr .env  # Windows
```

**2. Check .env format:**
```env
# ✅ CORRECT
GROQ_API_KEY=gsk_abc123

# ❌ WRONG (no spaces around =)
GROQ_API_KEY = gsk_abc123

# ❌ WRONG (no quotes needed)
GROQ_API_KEY="gsk_abc123"
```

**3. Verify loading in config.py:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Must be called before os.getenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment")
```

### Prevention
- Use `.env.example` as template
- Add validation in config.py
- Check environment with `echo $GROQ_API_KEY` (Linux) or `$env:GROQ_API_KEY` (Windows)

---

## Debugging Strategies

### Enable Verbose Logging
```python
import logging

# In server.py or config.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In llm_client.py
logger = logging.getLogger(__name__)
logger.debug(f"Calling LLM with key_index={key_index}")
```

### Test LLM Client Independently
```python
# test.py
import asyncio
from llm_client import call_llm

async def test():
    response = await call_llm(
        prompt="Say hello",
        system="You are a helpful assistant",
        key_index=0
    )
    print(response)

asyncio.run(test())
```

### Verify MongoDB Connection
```python
# test.py
import asyncio
from memory import MemoryStore

async def test():
    memory = MemoryStore(mongo_uri)
    session_id = "test123"
    await memory.save_session(session_id, {"goal": "test"})
    session = await memory.get_session(session_id)
    print(session)

asyncio.run(test())
```

### Check LangGraph State
```python
# Add debug prints in nodes
async def node_developer(state: PipelineState):
    print(f"DEBUG: State keys: {state.keys()}")
    print(f"DEBUG: Research length: {len(state.get('research', ''))}")
    result = await self.developer.execute(...)
    return {"developer": result}
```

---

## Known Limitations & Workarounds

### LangGraph Doesn't Support Parallel Nodes
**Workaround**: Use `asyncio.gather()` within a node:
```python
async def node_parallel(state):
    dev, research = await asyncio.gather(
        developer.execute(...),
        ceo.do_research(...)
    )
    return {"developer": dev, "research": research}
```

### Groq API Context Window (8192 tokens)
**Workaround**: Truncate long documents in validation:
```python
document_truncated = document[:4000]  # ~3000 tokens
await confidence.evaluate_and_store(..., document_truncated, ...)
```

### MongoDB Atlas Free Tier (512 MB)
**Workaround**: Add TTL index for auto-cleanup:
```python
# In memory.py
await db.sessions.create_index("created_at", expireAfterSeconds=2592000)  # 30 days
```

---

## Error Recovery Patterns

### Retry with Exponential Backoff
```python
import asyncio

async def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(wait_time)
```

### Graceful Degradation
```python
async def node_validation(state):
    try:
        confidence = await confidence_agent.evaluate_and_store(...)
        return {"confidence": confidence}
    except Exception as e:
        # Continue pipeline with warning
        return {
            "confidence": {
                "error": str(e),
                "confidence_score": 0,
                "hallucination_risk": "unknown"
            }
        }
```

---

## Getting Help

### Useful Resources
- **LangGraph Issues**: https://github.com/langchain-ai/langgraph/issues
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Groq Community**: https://discord.gg/groq
- **MongoDB Forums**: https://www.mongodb.com/community/forums/

### Debugging Checklist
- [ ] Check `.env` file exists and is loaded
- [ ] Verify all API keys are valid
- [ ] Test MongoDB connection independently
- [ ] Run from project root directory
- [ ] Check Python version (3.12+)
- [ ] Enable debug logging
- [ ] Test LLM client with simple prompt
- [ ] Verify LangGraph nodes registered before edges

---

## References

- [Architecture Documentation](architecture.md)
- [Technology Stack](tech_stack.md)
- [Workflow Details](workflows.md)

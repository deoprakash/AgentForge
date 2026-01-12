# API Reference

## REST API Documentation

AgentForge exposes a single REST endpoint for executing agent pipelines. This document provides complete API specifications, examples, and integration guides.

---

## Base URL

```
http://localhost:8000
```

**Production**: Replace `localhost` with your server's IP/domain

---

## Endpoints

### POST `/run`

Execute an AI agent pipeline to generate a document/report based on a natural language goal.

#### Request

**URL**: `/run`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body Schema**:
```json
{
  "command": "string (required)"
}
```

**Fields**:
- `command` (string, required): Natural language instruction containing:
  - Goal/task description
  - Optional: Email address for delivery (format: `send to email@example.com`)

**Example Requests**:
```json
{
  "command": "Write a proposal for warehouse optimization"
}
```

```json
{
  "command": "Create a report on AI trends in healthcare, send to doctor@hospital.com"
}
```

#### Response

**Status Code**: `200 OK` (even if pipeline has errors - check response body)

**Response Schema**:
```json
{
  "session_id": "string",
  "goal": "string",
  "email": "string | null",
  "plan": [
    {
      "step": "number",
      "task": "string",
      "description": "string"
    }
  ],
  "research": "string",
  "developer": "string",
  "writer": "string",
  "confidence": {
    "confidence_score": "number (0-100)",
    "confidence_reasoning": "string",
    "hallucination_risk": "low | medium | high",
    "hallucination_reasoning": "string"
  },
  "email_sent": "boolean",
  "created_at": "string (ISO 8601 datetime)"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique identifier for this execution (format: `ses_xxxxxxxx`) |
| `goal` | string | Extracted goal from command |
| `email` | string \| null | Extracted email address (null if not provided) |
| `plan` | array | Task breakdown from CEO agent |
| `plan[].step` | number | Sequential step number |
| `plan[].task` | string | Task title |
| `plan[].description` | string | Task details |
| `research` | string | Research findings (500-1000 words) |
| `developer` | string | Technical artifacts (Mermaid diagrams, architecture) |
| `writer` | string | Final document/proposal (500+ words) |
| `confidence.confidence_score` | number | Quality score (0-100, higher is better) |
| `confidence.confidence_reasoning` | string | Explanation of score |
| `confidence.hallucination_risk` | string | Risk level: "low", "medium", or "high" |
| `confidence.hallucination_reasoning` | string | Explanation of risk assessment |
| `email_sent` | boolean | Whether email was successfully delivered |
| `created_at` | string | ISO 8601 timestamp of execution start |

**Example Response**:
```json
{
  "session_id": "ses_a3f7b2c1",
  "goal": "Write a proposal for warehouse optimization",
  "email": "john@example.com",
  "plan": [
    {
      "step": 1,
      "task": "Analyze current warehouse layout",
      "description": "Conduct site assessment and workflow analysis"
    },
    {
      "step": 2,
      "task": "Research automation solutions",
      "description": "Investigate AGVs, robotics, and WMS platforms"
    }
  ],
  "research": "Warehouse optimization requires a holistic approach...\n\nKey findings:\n1. U-flow layouts improve picking efficiency by 25%\n2. AGV implementation reduces labor costs by 30%\n3. WMS integration provides real-time inventory visibility...",
  "developer": "```mermaid\ngraph TD\n  A[Receiving] --> B[Storage]\n  B --> C[Picking]\n  C --> D[Packing]\n  D --> E[Shipping]\n```\n\nTechnical Architecture:\n- Zone-based storage system\n- RFID tracking for inventory\n- Cloud-based WMS dashboard...",
  "writer": "# Warehouse Optimization Proposal\n\n## Executive Summary\nThis proposal outlines a comprehensive strategy to modernize warehouse operations...\n\n## Background\nCurrent challenges include:\n- Manual picking processes causing delays\n- Inefficient layout leading to long travel distances\n- Limited inventory visibility...\n\n## Proposed Solution\n1. Implement U-flow layout design\n2. Deploy automated guided vehicles (AGVs)\n3. Integrate warehouse management system (WMS)...",
  "confidence": {
    "confidence_score": 85,
    "confidence_reasoning": "Document aligns well with goal, includes research-backed solutions, clear structure, actionable recommendations",
    "hallucination_risk": "low",
    "hallucination_reasoning": "All claims are supported by research findings, no fabricated statistics or unverified technologies mentioned"
  },
  "email_sent": true,
  "created_at": "2024-01-15T10:30:45.123456Z"
}
```

---

## Error Responses

### 422 Unprocessable Entity

**Cause**: Invalid request body (missing required fields, wrong types)

**Example**:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "command"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

**Solution**: Ensure `command` field is present and is a string

---

### 500 Internal Server Error

**Cause**: Pipeline execution error (LLM API failure, database error, etc.)

**Example**:
```json
{
  "detail": "Internal server error"
}
```

**Solution**: Check server logs for detailed error trace

---

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Write a proposal for AI-powered customer service, send to ceo@company.com"
  }'
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/run"
payload = {
    "command": "Write a technical report on blockchain scalability"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Session ID: {result['session_id']}")
print(f"Confidence: {result['confidence']['confidence_score']}%")
print(f"\nDocument Preview:\n{result['writer'][:200]}...")
```

### Python (httpx async)

```python
import httpx
import asyncio

async def run_agent():
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/run",
            json={"command": "Create a marketing strategy for SaaS product"}
        )
        return response.json()

result = asyncio.run(run_agent())
```

### JavaScript (fetch)

```javascript
const response = await fetch("http://localhost:8000/run", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    command: "Write a grant proposal for climate research, send to grants@foundation.org"
  })
});

const result = await response.json();
console.log(`Confidence: ${result.confidence.confidence_score}%`);
console.log(`Email sent: ${result.email_sent}`);
```

### Postman

**Request**:
- Method: `POST`
- URL: `http://localhost:8000/run`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
  ```json
  {
    "command": "Write a product roadmap for mobile app"
  }
  ```

**Expected Response**: 200 OK with full pipeline results

---

## Command Parsing

The API automatically extracts goal and email from the `command` string using regex patterns.

### Email Extraction

**Patterns Recognized**:
- `send to email@example.com`
- `email to user@domain.com`
- `send email to contact@company.org`
- Standalone: `user@example.com` (at end of command)

**Examples**:
```python
# With explicit "send to"
command = "Write proposal, send to john@acme.com"
# Extracted: goal="Write proposal", email="john@acme.com"

# With "email to"
command = "Create report, email to ceo@startup.io"
# Extracted: goal="Create report", email="ceo@startup.io"

# Email at end
command = "Draft marketing plan for jane@company.com"
# Extracted: goal="Draft marketing plan for", email="jane@company.com"

# No email
command = "Write technical documentation"
# Extracted: goal="Write technical documentation", email=None
```

**Regex Pattern**:
```python
r'(?:send (?:to |email )?|email to )?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
```

---

## Email Integration

### Prerequisites

To enable email delivery, configure environment variables:

```env
EMAIL_ENABLED=true
ALLOW_EMAIL_SENDING=true
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Gmail App Password Setup**:
1. Enable 2-Factor Authentication on Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Copy 16-character password to `.env`

### Email Content

**Subject**: `AgentForge Report: {goal_first_50_chars}`

**Body**:
```
{writer_output}

---
Quality Metrics:
- Confidence Score: {confidence_score}%
- Hallucination Risk: {hallucination_risk}
```

**SMTP Configuration**:
- Server: `smtp.gmail.com`
- Port: `587` (STARTTLS)
- Authentication: App Password

### Email Status

Check `email_sent` field in response:
- `true`: Email successfully delivered
- `false`: Email not sent (either no email provided or delivery failed)

**Note**: Email failures don't stop pipeline execution. Check server logs for SMTP errors.

---

## Rate Limits

### LLM API (Groq)
- **Limit**: 90 requests/minute (30 per key × 3 keys)
- **Strategy**: Fixed key routing per agent
- **Pacing**: 0.4s global interval + 2s state delays
- **Status**: Automatically handled by client

### FastAPI Server
- **Limit**: No enforced limit (CPU-bound)
- **Recommendation**: Use reverse proxy (Nginx) for rate limiting in production

### MongoDB Atlas (Free Tier)
- **Connections**: 100 concurrent
- **Storage**: 512 MB

**Effect on Response Time**: 30-50 seconds per request (LLM generation dominates)

---

## Performance Benchmarks

### Typical Request Breakdown

| Stage | Duration | API Calls |
|-------|----------|-----------|
| CEO + Research | 8-12s | 1 (Key 1) |
| Developer | 5-8s | 1 (Key 2) |
| Writer | 10-15s | 1 (Key 3) |
| Validation | 3-5s | 1 (Key 1) |
| Email (optional) | 1-2s | 0 |
| **Total** | **33-48s** | **4** |

**Optimization Notes**:
- Combined operations reduce calls from 12 → 4 (67% reduction)
- Fixed key routing prevents rate limit bottlenecks
- Async I/O enables concurrent request handling

---

## Session Management

### Session ID Format
`ses_xxxxxxxx` (8 random hex characters)

**Example**: `ses_a3f7b2c1`

### Session Persistence

All executions stored in MongoDB with full state:

**Collections**:
- `sessions`: Request metadata (goal, email, timestamps)
- `plans`: CEO task breakdowns
- `research`: Research findings
- `documents`: Final writer outputs
- `actions`: Email deliveries + confidence reports

**Retrieval** (Future Feature):
```python
# Not yet implemented
GET /sessions/{session_id}
```

---

## Advanced Integration

### Webhook Delivery (Future)

*Not yet implemented - roadmap feature*

**Concept**:
```env
WEBHOOK_URL=https://yourapp.com/agent-complete
WEBHOOK_SECRET=your_hmac_secret
```

**Payload**:
```json
{
  "event": "pipeline.complete",
  "session_id": "ses_abc123",
  "timestamp": "2024-01-15T10:30:45Z",
  "result": { ... }
}
```

### Streaming Responses (Future)

*Not yet implemented - roadmap feature*

**Concept**: Server-Sent Events (SSE) for real-time progress

```
GET /run/stream?command=...

event: plan
data: {"plan": [...]}

event: research
data: {"research": "..."}

event: writer
data: {"writer": "..."}

event: complete
data: {"confidence": {...}}
```

---

## OpenAPI Schema

FastAPI automatically generates OpenAPI documentation:

**Interactive Docs**: http://localhost:8000/docs  
**OpenAPI JSON**: http://localhost:8000/openapi.json

**Features**:
- Interactive "Try it out" testing
- Request/response schema visualization
- cURL command generation

---

## Security Considerations

### Input Validation
- ✅ `command` string validated by Pydantic
- ✅ Max length: No enforced limit (recommend < 1000 chars)
- ✅ Special characters: Allowed (LLM handles sanitization)

### Injection Risks
- **SQL Injection**: Not applicable (MongoDB uses BSON)
- **Prompt Injection**: LLM-level risk (mitigated by system prompts)
- **Email Injection**: Validated email regex prevents header injection

### Authentication
- ❌ **Not Implemented**: No API key required (current version)
- 🔒 **Recommendation**: Add API key middleware for production

**Example** (Future):
```python
from fastapi import Header, HTTPException

@app.post("/run")
async def run(req: RunRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid API key")
```

### HTTPS
- ❌ **HTTP only** in development
- 🔒 **Production**: Use reverse proxy (Nginx) with SSL/TLS

---

## Error Handling Best Practices

### Client-Side Retry Logic

```python
import time

def call_agent_with_retry(command, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/run",
                json={"command": command},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
        except requests.HTTPError as e:
            if e.response.status_code >= 500:
                # Server error - retry
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
            else:
                # Client error - don't retry
                raise
```

### Timeout Configuration

**Recommended Timeouts**:
- Connection timeout: 10s
- Read timeout: 60s (pipeline takes 30-50s)

```python
# Python requests
response = requests.post(url, json=payload, timeout=(10, 60))

# JavaScript fetch
const controller = new AbortController();
setTimeout(() => controller.abort(), 60000);
fetch(url, { signal: controller.signal, ... })
```

---

## Monitoring & Logging

### Response Time Tracking

```python
import time

start = time.time()
response = requests.post("http://localhost:8000/run", json={"command": "..."})
elapsed = time.time() - start

print(f"Response time: {elapsed:.2f}s")
```

### Quality Metrics Dashboard

```python
results = []

for goal in goals:
    response = requests.post(url, json={"command": goal})
    data = response.json()
    
    results.append({
        "goal": goal,
        "confidence": data["confidence"]["confidence_score"],
        "hallucination_risk": data["confidence"]["hallucination_risk"],
        "duration": elapsed
    })

# Calculate averages
avg_confidence = sum(r["confidence"] for r in results) / len(results)
print(f"Average confidence: {avg_confidence:.1f}%")
```

---

## Testing

### Unit Test Example (pytest)

```python
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_run_endpoint():
    response = client.post("/run", json={
        "command": "Write a test document"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert data["goal"] == "Write a test document"
    assert data["email"] is None
    assert "writer" in data
    assert data["confidence"]["confidence_score"] >= 0
    assert data["confidence"]["confidence_score"] <= 100

def test_email_extraction():
    response = client.post("/run", json={
        "command": "Write report, send to test@example.com"
    })
    
    data = response.json()
    assert data["email"] == "test@example.com"
```

### Load Testing (locust)

```python
from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def run_agent(self):
        self.client.post("/run", json={
            "command": "Write a short summary of AI trends"
        })
```

**Run**:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Migration from Legacy Orchestrator

If you have code using the old `orchestrator.py`:

**Old Code**:
```python
from orchestrator import Orchestrator
orchestrator = Orchestrator(...)
```

**New Code**:
```python
from orchestrator_langgraph import OrchestratorLangGraph
orchestrator = OrchestratorLangGraph(...)
```

**Environment Variable**:
```env
USE_LANGGRAPH=true  # Enables LangGraph orchestrator
```

---

## References

- [Architecture Documentation](architecture.md)
- [Workflow Details](workflows.md)
- [Troubleshooting Guide](troubleshooting.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)

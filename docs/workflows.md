# AgentForge Workflows

## Complete Execution Flow

This document details the step-by-step execution workflows in AgentForge, including timing, state transitions, and data transformations.

---

## 1. Request Lifecycle

### Step 1: HTTP Request Reception
```
POST http://localhost:8000/run
Content-Type: application/json

{
  "command": "Write a proposal for optimizing warehouse operations, send to john@example.com"
}
```

**Processing**:
1. FastAPI receives request
2. Pydantic validates `RunRequest` schema
3. `parse_command()` extracts goal + email using regex
4. Orchestrator selected based on `USE_LANGGRAPH` flag

---

### Step 2: Session Initialization
```python
# orchestrator_langgraph.py
session_id = f"ses_{uuid.uuid4().hex[:8]}"
await self.memory.save_session(session_id, {"goal": goal, "email": email})
```

**MongoDB Document**:
```json
{
  "_id": ObjectId("..."),
  "session_id": "ses_a3f7b2c1",
  "goal": "Write a proposal for optimizing warehouse operations",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 2. LangGraph Pipeline Execution

### State Machine Diagram
```
              ┌─────────────────┐
              │   START         │
              └────────┬────────┘
                       │ 0s delay
                       ▼
              ┌─────────────────┐
              │ CEO+RESEARCH    │◀── Key 1 (index 0)
              │ Combined Call   │
              └────────┬────────┘
                       │ 2s delay
                       ▼
              ┌─────────────────┐
              │ DEVELOPER       │◀── Key 2 (index 1)
              │ Technical Docs  │
              └────────┬────────┘
                       │ 2s delay
                       ▼
              ┌─────────────────┐
              │ WRITER          │◀── Key 3 (index 2)
              │ Final Document  │
              └────────┬────────┘
                       │ 2s delay
                       ▼
              ┌─────────────────┐
              │ VALIDATION      │◀── Key 1 (index 0)
              │ Quality Check   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   END           │
              └─────────────────┘
```

---

### Node 1: CEO + Research (Combined)

**Timing**: 0s delay (entry node)  
**API Key**: Key 1 (index 0)  
**Purpose**: Strategic planning + initial research in **single API call**

**Input State**:
```python
{
  "session_id": "ses_a3f7b2c1",
  "goal": "Write a proposal for optimizing warehouse operations",
  "plan": None,
  "research": None,
  "developer": None,
  "writer": None,
  "confidence": None
}
```

**Execution**:
```python
# agents/ceo.py
async def create_plan_and_research(self, goal: str, key_index: int | None = None):
    prompt = f"""
    Goal: {goal}
    
    Provide a JSON with:
    1. "plan": Array of task objects
    2. "research": Key research findings
    """
    combined = await self.think(prompt, purpose="generation", key_index=key_index)
    parsed = json.loads(combined)
    return parsed["plan"], parsed["research"]
```

**LLM Call Details**:
- **Model**: llama-3.1-8b-instant
- **Temperature**: 0.7
- **System Prompt**: "you are the CEO agent."
- **Output**: JSON with plan array + research string

**Output State Update**:
```python
{
  "plan": [
    {"step": 1, "task": "Analyze current warehouse layout"},
    {"step": 2, "task": "Research automation solutions"}
  ],
  "research": "Warehouse optimization requires: 1) Layout efficiency (U-flow/L-flow), 2) Automation (AGVs, robotics), 3) WMS integration..."
}
```

**MongoDB Persistence**:
```python
await memory.save_plan(session_id, plan)
await memory.save_research(session_id, research)
```

**API Call Count**: 1 (combined CEO+Research)

---

### Node 2: Developer

**Timing**: 2s delay after CEO+Research  
**API Key**: Key 2 (index 1)  
**Purpose**: Generate technical artifacts (diagrams, architectures)

**Input State**:
```python
{
  "session_id": "ses_a3f7b2c1",
  "goal": "...",
  "plan": [...],
  "research": "...",
  "developer": None  # ← To be populated
}
```

**Execution**:
```python
# agents/developer.py
async def execute(self, task: str, key_index: int | None = None):
    prompt = f"""
    Task: {task}
    
    Generate:
    1. Mermaid diagram (warehouse layout)
    2. Technical architecture outline
    3. Implementation checklist
    """
    return await self.think(prompt, purpose="generation", key_index=key_index)
```

**LLM Call Details**:
- **Model**: llama-3.1-8b-instant
- **Temperature**: 0.7
- **System Prompt**: "you are the developer agent."
- **Output**: Mermaid syntax + technical documentation

**Output State Update**:
```python
{
  "developer": """
  ```mermaid
  graph TD
    A[Receiving] --> B[Storage]
    B --> C[Picking]
    C --> D[Packing]
  ```
  
  Technical Architecture:
  - Zone-based storage system
  - RFID tracking integration
  - Real-time inventory dashboard
  """
}
```

**API Call Count**: 1

---

### Node 3: Writer

**Timing**: 2s delay after Developer  
**API Key**: Key 3 (index 2)  
**Purpose**: Generate final formatted document/proposal

**Input State**:
```python
{
  "session_id": "ses_a3f7b2c1",
  "goal": "...",
  "research": "...",
  "developer": "...",
  "writer": None  # ← To be populated
}
```

**Execution**:
```python
# agents/writer.py
async def execute(self, task: str, key_index: int | None = None):
    prompt = f"""
    Task: {task}
    Research: {research}
    Technical Artifacts: {developer}
    
    Write a professional proposal with:
    - Executive Summary
    - Background & Research
    - Proposed Solution
    - Implementation Plan
    - Cost-Benefit Analysis
    """
    return await self.think(prompt, purpose="generation", key_index=key_index)
```

**LLM Call Details**:
- **Model**: llama-3.1-8b-instant
- **Temperature**: 0.7
- **System Prompt**: "you are the writer agent."
- **Output**: Formatted proposal document

**Output State Update**:
```python
{
  "writer": """
  # Warehouse Optimization Proposal
  
  ## Executive Summary
  This proposal outlines a comprehensive strategy to optimize warehouse operations...
  
  ## Background & Research
  Current state analysis reveals inefficiencies in layout and manual processes...
  
  ## Proposed Solution
  1. Implement U-flow layout design
  2. Integrate automated guided vehicles (AGVs)
  3. Deploy warehouse management system (WMS)
  
  [Full 500+ word document]
  """
}
```

**MongoDB Persistence**:
```python
await memory.save_document(session_id, writer_output)
```

**API Call Count**: 1

---

### Node 4: Validation

**Timing**: 2s delay after Writer  
**API Key**: Key 1 (index 0)  
**Purpose**: Quality validation (confidence + hallucination detection in **single call**)

**Input State**:
```python
{
  "session_id": "ses_a3f7b2c1",
  "goal": "...",
  "writer": "...",
  "confidence": None  # ← To be populated
}
```

**Execution**:
```python
# agents/confidence.py
async def evaluate_and_store(self, goal: str, document: str, session_id: str, key_index: int | None = None):
    prompt = f"""
    Goal: {goal}
    Document: {document[:500]}...
    
    Evaluate and return JSON:
    {
      "confidence_score": 0-100,
      "confidence_reasoning": "...",
      "hallucination_risk": "low|medium|high",
      "hallucination_reasoning": "..."
    }
    """
    result = await self.think(prompt, purpose="validation", key_index=key_index)
    parsed = json.loads(result)
    
    # Store in MongoDB
    await self.memory.save_action(session_id, {
        "type": "confidence_report",
        "confidence_score": parsed["confidence_score"],
        "hallucination_risk": parsed["hallucination_risk"],
        "details": parsed
    })
    
    return parsed
```

**LLM Call Details**:
- **Model**: llama-3.1-8b-instant
- **Temperature**: 0.3 (lower for validation consistency)
- **System Prompt**: "you are the confidence agent."
- **Output**: JSON with quality metrics

**Output State Update**:
```python
{
  "confidence": {
    "confidence_score": 85,
    "confidence_reasoning": "Document aligns with goal, includes research-backed solutions, logical structure",
    "hallucination_risk": "low",
    "hallucination_reasoning": "All claims supported by research findings, no fabricated statistics"
  }
}
```

**Console Output**:
```
Confidence Score: 85%
Hallucination Risk: low
```

**API Call Count**: 1 (combined confidence+hallucination)

---

## 3. Post-Processing

### Email Delivery (Optional)
```python
# agents/automation.py
if email and allow_email_sending:
    email_body = f"""
    {writer_output}
    
    ---
    Quality Metrics:
    - Confidence: {confidence_score}%
    - Hallucination Risk: {hallucination_risk}
    """
    
    await self.gmail.send_email(
        to=email,
        subject=f"AgentForge Report: {goal[:50]}",
        body=email_body
    )
    
    await memory.save_action(session_id, {
        "type": "email_sent",
        "to": email,
        "timestamp": datetime.now()
    })
```

---

### Response Assembly
```python
# server.py
result = {
    "session_id": session_id,
    "goal": goal,
    "plan": plan,
    "research": research,
    "developer": developer,
    "writer": writer,
    "confidence": confidence,
    "email_sent": email is not None,
    "created_at": datetime.now().isoformat()
}

return JSONResponse(serialize_doc(result))
```

---

## 4. Timing Analysis

### Total Pipeline Duration (Typical):
```
CEO+Research:  ~8-12s (LLM generation)
Delay:         +2s
Developer:     ~5-8s (LLM generation)
Delay:         +2s
Writer:        ~10-15s (LLM generation)
Delay:         +2s
Validation:    ~3-5s (LLM evaluation)
Email:         ~1-2s (SMTP)
-------------------------------------------
Total:         ~33-48s per request
```

### API Call Breakdown:
| Node | API Calls | Key Used |
|------|-----------|----------|
| CEO+Research | 1 | Key 1 |
| Developer | 1 | Key 2 |
| Writer | 1 | Key 3 |
| Validation | 1 | Key 1 |
| **TOTAL** | **4** | 3 keys |

**Optimization Impact**: Reduced from 12 calls (legacy) to 4 calls = **67% reduction**

---

## 5. Error Handling Workflow

### Retry Logic (Per Node):
```python
async def node_with_retry(state: PipelineState, max_retries=2):
    for attempt in range(max_retries):
        try:
            result = await agent.execute(task, key_index=index)
            return {"output": result}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"output": f"ERROR: {str(e)}"}
            await asyncio.sleep(1)  # Exponential backoff
```

### LLM Client Backoff:
```python
# llm_client.py
if response.status_code == 429:  # Rate limit
    await asyncio.sleep(min_interval * 2)
    return await call_llm(...)  # Retry once
elif response.status_code >= 500:
    raise Exception(f"LLM service error: {response.status_code}")
```

---

## 6. Alternative Workflows

### Conditional Routing (Future Enhancement):
```python
def route_after_validation(state: PipelineState):
    confidence = state["confidence"]["confidence_score"]
    hallucination = state["confidence"]["hallucination_risk"]
    
    if confidence < 70 or hallucination == "high":
        return "retry_writer"  # Go back to writer
    else:
        return "end"  # Proceed to completion
```

### Parallel Execution (Not Implemented):
```
     CEO+RESEARCH
          │
    ┌─────┴─────┐
    ▼           ▼
 DEVELOPER   WRITER
    └─────┬─────┘
          ▼
     VALIDATION
```
*Note: Sequential execution chosen for state dependency (writer needs developer output)*

---

## 7. State Persistence Strategy

### Checkpoint Pattern:
- After each node, state saved to MongoDB
- Enables recovery from failures mid-pipeline
- Session_id tracks entire execution

### MongoDB Collections Used:
```
sessions       → Initial request metadata
plans          → CEO output (tasks)
research       → CEO output (findings)
documents      → Writer output (final doc)
actions        → Validation + email logs
```

---

## 8. Quality Gates

### Current Implementation:
- Validation runs at END (no blocking)
- Metrics printed to console
- Metrics appended to email

### Recommended Enhancement:
```python
# Add conditional edge after validation
graph.add_conditional_edges(
    "validation",
    route_after_validation,
    {
        "retry_writer": "writer",
        "end": END
    }
)
```

This would enable automatic retry loops for low-quality outputs.

---

## 9. Load Balancing Workflow

### Key Selection Strategy:
```
Request → Parse Goal → Initialize Session → LangGraph Start

Node 1 (CEO+Research)     → call_llm(key_index=0)  [Key 1]
       ↓ (2s delay)
Node 2 (Developer)        → call_llm(key_index=1)  [Key 2]
       ↓ (2s delay)
Node 3 (Writer)           → call_llm(key_index=2)  [Key 3]
       ↓ (2s delay)
Node 4 (Validation)       → call_llm(key_index=0)  [Key 1]
       ↓
End → Response
```

### Rate Limit Protection:
- **Global pacing**: 0.4s minimum between ANY LLM calls
- **Per-key tracking**: Last call timestamp stored
- **State delays**: 2s between nodes for natural pacing
- **Strategy**: Fixed routing prevents key exhaustion

---

## References

- [Architecture Overview](architecture.md)
- [Troubleshooting Guide](troubleshooting.md)
- [API Reference](api_reference.md)

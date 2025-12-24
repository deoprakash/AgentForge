# import uvicorn
# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, model_validator
# from orchestrator import Orchestrator
# from memory import MemoryStore
# from config import APP_HOST, APP_PORT, MONGO_URI
# from utils import serialize_doc, parse_command

# app = FastAPI()
# memory = MemoryStore(MONGO_URI)
# orchestrator = Orchestrator(memory)

# class RunRequest(BaseModel):
#     command: str | None = None
#     goal: str | None = None
#     email: str | None = None

#     @model_validator(mode="after")
#     def ensure_input(self):
#         if self.command:
#             return self
#         if self.goal and self.email:
#             return self
#         raise ValueError("Provide either 'command' or both 'goal' and 'email'.")

# class RunLegacyRequest(BaseModel):
#     goal: str
#     email: str

# @app.post("/run")
# async def run(req: RunRequest):
#     try:
#         if req.command:
#             parsed = parse_command(req.command)
#             goal, email = parsed["goal"], parsed["email"]
#         else:
#             goal, email = req.goal, req.email

#         if not goal or not email:
#             raise ValueError("Both 'goal' and 'email' are required when no command is provided.")

#         result = await orchestrator.run(goal, email)
#         return JSONResponse(content=serialize_doc(result))
#     except ValueError as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})

# @app.post("/run/legacy")
# async def run_legacy(req: RunLegacyRequest):
#     result = await orchestrator.run(req.goal, req.email)
#     return JSONResponse(content=serialize_doc(result))

# if __name__ == "__main__":
#     uvicorn.run("server:app", host=APP_HOST, port=APP_PORT, reload=True)

# ------------------------------ Human in loop ----------------------------------

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator
from orchestrator import Orchestrator
from memory import MemoryStore
from config import APP_HOST, APP_PORT, MONGO_URI, LLM_PROVIDER
from utils import serialize_doc, parse_command

app = FastAPI()
memory = MemoryStore(MONGO_URI)
orchestrator = Orchestrator(memory)


# ===============================
# Health
# ===============================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm_provider": LLM_PROVIDER,
    }


# ===============================
# Request Models
# ===============================

class RunRequest(BaseModel):
    command: str | None = None
    goal: str | None = None
    email: str | None = None

    @model_validator(mode="after")
    def ensure_input(self):
        if self.command:
            return self
        if self.goal:
            return self
        raise ValueError("Provide either 'command' or 'goal'.")


class RunLegacyRequest(BaseModel):
    goal: str
    email: str


class ApprovalRequest(BaseModel):
    session_id: str
    decision: str  # retry_now | retry_later | cancel


# ===============================
# Main Run Endpoint
# ===============================

@app.post("/run")
async def run(req: RunRequest):
    try:
        if req.command:
            parsed = parse_command(req.command)
            goal, email = parsed.get("goal"), parsed.get("email")
        else:
            goal, email = req.goal, req.email

        if not goal:
            raise ValueError("'goal' is required when no command is provided.")

        result = await orchestrator.run(goal, email)

        # If the run returned an LLM sentinel status, map to a proper HTTP code.
        if isinstance(result, dict):
            message = str(result.get("message", ""))
            if "__LLM_RATE_LIMITED__" in message:
                return JSONResponse(status_code=429, content=serialize_doc(result))

        return JSONResponse(content=serialize_doc(result))

    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    except Exception as e:
        # Avoid crashing the server on upstream LLM/network errors.
        text = str(e)
        status = 500
        if "429" in text or "Too Many Requests" in text:
            status = 429
        return JSONResponse(status_code=status, content={"error": "Request failed", "detail": text})


@app.post("/run/legacy")
async def run_legacy(req: RunLegacyRequest):
    result = await orchestrator.run(req.goal, req.email)
    return JSONResponse(content=serialize_doc(result))


# ===============================
# 🧠 Human-in-the-Loop Approval
# ===============================

@app.post("/approve")
async def approve(req: ApprovalRequest):
    decision = req.decision.lower()

    if decision not in ["retry_now", "retry_later", "cancel"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid decision. Use retry_now, retry_later, or cancel."}
        )

    # Save human decision
    await memory.save_actions(req.session_id, {
        "type": "human_in_loop",
        "status": "RESOLVED",
        "decision": decision
    })

    # Handle decision
    if decision == "retry_now":
        result = await orchestrator.resume(req.session_id)
        return JSONResponse(content={
            "status": "RESUMED",
            "result": serialize_doc(result)
        })

    if decision == "retry_later":
        return JSONResponse(content={
            "status": "PAUSED",
            "message": "Session remains paused. Retry later."
        })

    if decision == "cancel":
        return JSONResponse(content={
            "status": "CANCELLED",
            "message": "Session cancelled by human."
        })


# ===============================
# Server Entrypoint
# ===============================

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True
    )

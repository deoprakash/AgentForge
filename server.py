import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, model_validator
from orchestrator import Orchestrator
from memory import MemoryStore
from config import APP_HOST, APP_PORT, MONGO_URI
from utils import serialize_doc, parse_command

app = FastAPI()
memory = MemoryStore(MONGO_URI)
orchestrator = Orchestrator(memory)

class RunRequest(BaseModel):
    command: str | None = None
    goal: str | None = None
    email: str | None = None

    @model_validator(mode="after")
    def ensure_input(self):
        if self.command:
            return self
        if self.goal and self.email:
            return self
        raise ValueError("Provide either 'command' or both 'goal' and 'email'.")

class RunLegacyRequest(BaseModel):
    goal: str
    email: str

@app.post("/run")
async def run(req: RunRequest):
    try:
        if req.command:
            parsed = parse_command(req.command)
            goal, email = parsed["goal"], parsed["email"]
        else:
            goal, email = req.goal, req.email

        if not goal or not email:
            raise ValueError("Both 'goal' and 'email' are required when no command is provided.")

        result = await orchestrator.run(goal, email)
        return JSONResponse(content=serialize_doc(result))
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/run/legacy")
async def run_legacy(req: RunLegacyRequest):
    result = await orchestrator.run(req.goal, req.email)
    return JSONResponse(content=serialize_doc(result))

if __name__ == "__main__":
    uvicorn.run("server:app", host=APP_HOST, port=APP_PORT, reload=True)
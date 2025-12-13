import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from orchestrator import Orchestrator
from memory import MemoryStore
from config import APP_HOST, APP_PORT, MONGO_URI
from utils import serialize_doc, parse_command

app = FastAPI()
memory = MemoryStore(MONGO_URI)
orchestrator = Orchestrator(memory)

class RunRequest(BaseModel):
    command: str

class RunLegacyRequest(BaseModel):
    goal: str
    email: str

@app.post("/run")
async def run(req: RunRequest):
    try:
        parsed = parse_command(req.command)
        result = await orchestrator.run(parsed["goal"], parsed["email"])
        return JSONResponse(content=serialize_doc(result))
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/run/legacy")
async def run_legacy(req: RunLegacyRequest):
    result = await orchestrator.run(req.goal, req.email)
    return JSONResponse(content=serialize_doc(result))

if __name__ == "__main__":
    uvicorn.run("server:app", host=APP_HOST, port=APP_PORT, reload=True)
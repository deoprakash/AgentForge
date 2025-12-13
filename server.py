import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from orchestrator import Orchestrator
from memory import MemoryStore
from config import APP_HOST, APP_PORT

app = FastAPI()
memory = MemoryStore()
orchestrator = Orchestrator(memory)

class RunRequest(BaseModel):
    goal: str
    email: str

@app.post("/run")
async def run(req: RunRequest):
    return await orchestrator.run(req.goal, req.email)

if __name__ == "__main__":
    uvicorn.run("server:app", host=APP_HOST, port=APP_PORT, reload=True)
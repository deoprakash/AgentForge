from llm_client import call_llm

class BaseAgent:
    def __init__(self, name, memory):
        self.name = name
        self.memory = memory

    async def think(self, prompt: str, purpose: str = "generation", key_index: int | None = None):
        system = f"you are the {self.name} agent."
        return await call_llm(prompt, system, purpose=purpose, key_index=key_index)
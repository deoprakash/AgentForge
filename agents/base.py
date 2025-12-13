from llm_client import call_llm

class BaseAgent:
    def __init__(self, name, memory):
        self.name = name
        self.memory = memory

    async def think(self, prompt:str):
        system = f"you are the {self.name} agent."
        return await call_llm(prompt, system)
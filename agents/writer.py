from agents.base import BaseAgent

class WriterAgent(BaseAgent):
    async def write_document(self, brief:str):
        return {"document": await self.think(brief)}
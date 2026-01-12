from agents.base import BaseAgent

class WriterAgent(BaseAgent):
    async def write_document(self, brief: str, key_index: int | None = None):
        return {"document": await self.think(brief, key_index=key_index)}
from agents.base import BaseAgent
from tools.file_tool import FileTool

file_tool = FileTool()

class DeveloperAgent(BaseAgent):
    async def generate_diagram(self, instructions: str, key_index: int | None = None):
        mermaid = await self.think(instructions, key_index=key_index)
        saved = await file_tool.save("diagram.mmd", mermaid.encode())
        return {"mermaid": mermaid, "file": saved}
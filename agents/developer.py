from agents.base import BaseAgent
from tools.file_tool import FileTool

file_tool = FileTool()

class DeveloperAgent(BaseAgent):
    async def generate_diagram(self, instructions: str):
        mermaid = await self.think(instructions)
        saved = await file_tool.save("diagram.mmd", mermaid.encode())
        return {"mermaid": mermaid, "file": saved}
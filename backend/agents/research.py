from agents.base import BaseAgent
from tools.search_tool import SearchTool

search_tool = SearchTool()

class ResearchAgent(BaseAgent):
    async def run_research(self, topic: str):
        results = await search_tool.search(topic)
        summary = await self.think(f"Summarize: {results}")
        return {"results": results, "summary": summary}
    
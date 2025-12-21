from agents.base import BaseAgent

class ReviewerAgent(BaseAgent):
    async def review(self, document: str):
        prompt = f"""
        You are a Reviewer Agent.

        Review the following document for:
        - Clarity
        - Completeness
        - Professional tone
        - Missing sections
        - Grammar issues

        If the document is GOOD, respond with:
        APPROVED

        If it needs improvement, respond in JSON format:
        {{
            "status": "REVISE",
            "feedback": "Clear, actionable feedback for improvement"
        }}

        Document:
        ----------------
        {document}
        ----------------
        """

        response = await self.think(prompt)

        if "APPROVED" in response.upper():
            return {"status": "APPROVED", "feedback": None}

        return {
            "status": "REVISE",
            "feedback": response
        }

from agents.base import BaseAgent
import json

class ConfidenceAgent(BaseAgent):
    async def evaluate(self, document: str):
        prompt = f"""
        You are a Confidence & Hallucination Detection Agent.

        Evaluate the document below on:
        1. Factual consistency
        2. Unsupported claims
        3. Vagueness
        4. Overconfidence without evidence

        Return ONLY valid JSON in this format:

        {{
            "confidence_score": 0-100,
            "hallucination_risk": "LOW | MEDIUM | HIGH",
            "issues": [
                "issue 1",
                "issue 2"
            ],
            "verdict": "SAFE | REVISE | WARNING"
        }}

        Document:
        ----------------
        {document}
        ----------------
        """

        raw = await self.think(prompt)

        try:
            return json.loads(raw)
        except Exception:
            # Safe fallback
            return {
                "confidence_score": 40,
                "hallucination_risk": "HIGH",
                "issues": ["Failed to parse confidence evaluation"],
                "verdict": "REVISE"
            }

import json
import re

from agents.base import BaseAgent


class CEOAgent(BaseAgent):
    def _extract_json_from_text(self, text: str):
        """Extract a JSON object from LLM output (handles code fences / extra prose)."""
        text = (text or "").strip()
        if not text:
            return None

        # 1) Direct JSON
        try:
            parsed = json.loads(text)
            return parsed
        except Exception:
            pass

        # 2) JSON in markdown code block
        code_block = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1))
            except Exception:
                pass

        # 3) Best-effort: first {...} balanced braces
        start = text.find("{")
        if start == -1:
            return None

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except Exception:
                        return None

        return None

    async def create_plan(self, goal: str):
        prompt = f"""You are the CEO agent. Break the user's goal into a strict, sequential handoff across exactly three agents.

Return ONLY valid JSON with this exact structure and ordering:

{{
    "goal": "...",
    "tasks": [
        {{"assigned_agent": "Research", "description": "..."}},
        {{"assigned_agent": "Developer", "description": "..."}},
        {{"assigned_agent": "Writer", "description": "..."}}
    ]
}}

Rules:
- EXACTLY 3 tasks.
- EXACT order: Research first, then Developer, then Writer.
- assigned_agent must be EXACTLY one of: "Research", "Developer", "Writer".
- No other agents. Do NOT include Automation tasks.
- Research task: what to look up / summarize for the goal.
- Developer task: what technical artifact/structure is needed (can be a mermaid diagram or technical outline).
- Writer task: how to write the final response using the research + developer output.

User goal:
{goal}
"""
        raw = await self.think(prompt)
        print(f"DEBUG: Raw LLM response: {raw}")

        parsed = self._extract_json_from_text(raw)
        if parsed:
            print("DEBUG: Successfully extracted JSON plan")
            return parsed

        print("DEBUG: Could not extract JSON from response")
        return {
            "goal": goal,
            "tasks": [
                {
                    "assigned_agent": "Research",
                    "description": f"Research the topic and gather key facts for: {goal}",
                },
                {
                    "assigned_agent": "Developer",
                    "description": "Create a concise technical outline or mermaid diagram that structures the solution.",
                },
                {
                    "assigned_agent": "Writer",
                    "description": "Write the final response using the research and the technical outline.",
                },
            ],
        }
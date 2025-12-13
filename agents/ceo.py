import json 
import re
from agents.base import BaseAgent

class CEOAgent(BaseAgent):
    async def create_plan(self, goal:str):
        prompt = f"""Create a JSON plan with this exact structure. IMPORTANT: assigned_agent must be EXACTLY one of: "Research", "Writer", "Developer", or "Automation". Do NOT combine agent names.

{{"goal": "...", "tasks": [{{"assigned_agent": "Research", "description": "..."}}]}}

Valid agents:
- Research: For market research and information gathering
- Writer: For writing documents and content
- Developer: For creating diagrams and technical artifacts  
- Automation: For sending emails and automating processes

Goal: {goal}"""
        raw = await self.think(prompt)
        print(f"DEBUG: Raw LLM response: {raw}")
        
        try:
            # Try direct JSON parsing first
            return json.loads(raw)
        except:
            # If that fails, extract JSON from markdown code blocks
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    print(f"DEBUG: Extracted JSON: {json_str}")
                    return json.loads(json_str)
                except Exception as e:
                    print(f"DEBUG: JSON parse error after extraction: {e}")
                    return {"goal": goal, "tasks": []}
            else:
                print(f"DEBUG: Could not find JSON in response")
                return {"goal": goal, "tasks": []}
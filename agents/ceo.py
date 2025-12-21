import json 
import re
from agents.base import BaseAgent

class CEOAgent(BaseAgent):
    def _extract_json_from_text(self, text: str):
        """Extract and parse JSON from text, handling code blocks and nested structures."""
        # Try direct JSON parsing first
        try:
            return json.loads(text)
        except:
            pass
        
        # Try extracting from markdown code blocks
        code_block = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1))
            except:
                pass
        
        # Try finding JSON object by braces - find first { and match closing }
        start = text.find('{')
        if start != -1:
            # Count braces to find the matching closing brace
            brace_count = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            json_str = text[start:i+1]
                            return json.loads(json_str)
                        except:
                            pass
        
        return None
    
    async def create_plan(self, goal:str):
        prompt = f"""Create a JSON plan with this exact structure. IMPORTANT: assigned_agent must be EXACTLY one of: "Research", "Writer", or "Developer". Do NOT include Automation tasks.

{{"goal": "...", "tasks": [{{"assigned_agent": "Research", "description": "..."}}]}}

Valid agents:
- Research: For market research and information gathering
- Writer: For writing documents and content
- Developer: For creating diagrams and technical artifacts

Do NOT create multiple similar tasks. Create a focused plan that delivers one final output.

Goal: {goal}"""
        raw = await self.think(prompt)
        print(f"DEBUG: Raw LLM response: {raw}")
        
        parsed = self._extract_json_from_text(raw)
        if parsed:
            print(f"DEBUG: Successfully extracted JSON plan")
            return parsed
        else:
            print(f"DEBUG: Could not extract JSON from response")
            return {"goal": goal, "tasks": []}
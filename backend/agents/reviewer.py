import json
import re

from agents.base import BaseAgent

class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent: Actively improves documents for clarity, correctness, and consistency.
    """

    async def repair(
        self,
        original_document: str,
        detected_issues: list = None,
        user_revision_instruction: str = None,
        constraints: dict = None,
        key_index: int = 1
    ):
        # Force reviewer action even if no issues are detected
        issues_text = (
            "\n".join(f"- {issue}" for issue in detected_issues)
            if detected_issues
            else "- Perform a full editorial, grammar, clarity, and consistency review"
        )

        prompt = f"""
You are a professional Reviewer Agent.

MANDATORY RESPONSIBILITIES:
- Improve clarity, grammar, and professional tone
- Fix spelling, formatting, and syntax issues
- Reduce redundancy and vague phrasing
- Ensure internal and logical consistency
- Preserve original meaning and structure
- Do NOT introduce new facts, assumptions, or hallucinations
- You MUST make improvements even if no explicit issues are listed

{f'Additional instruction: {user_revision_instruction}' if user_revision_instruction else ''}
{f'Constraints: {json.dumps(constraints, indent=2)}' if constraints else ''}

Original Document:
{original_document}

Review Focus:
{issues_text}

Output ONLY the improved document.
"""

        revised_document = await self.think(
            prompt,
            purpose="review_improve",
            key_index=key_index
        )

        # Detect no-op reviewer behavior
        changes_made = revised_document.strip() != original_document.strip()

        return {
            "document": revised_document,
            "status": "improved",
            "changes_made": changes_made
        }

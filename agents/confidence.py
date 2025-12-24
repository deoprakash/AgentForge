from agents.base import BaseAgent
import json
import re


def _strip_code_fences(text: str) -> str:
    if not text:
        return text
    # Remove triple-backtick fences (``` or ```json)
    text = re.sub(r"^\s*```(?:json)?\s*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?\s*```\s*$", "", text)
    return text.strip()


def _extract_json_object(text: str) -> str | None:
    if not text:
        return None

    # Prefer the first JSON object if the model included extra prose.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start : end + 1].strip()
    return candidate if candidate.startswith("{") and candidate.endswith("}") else None


def _normalize_confidence_report(report: dict) -> dict:
    confidence_score = report.get("confidence_score", 40)
    try:
        confidence_score = int(confidence_score)
    except Exception:
        confidence_score = 40
    confidence_score = max(0, min(100, confidence_score))

    hallucination_risk = str(report.get("hallucination_risk", "HIGH")).upper().strip()
    if hallucination_risk not in {"LOW", "MEDIUM", "HIGH"}:
        hallucination_risk = "HIGH"

    issues = report.get("issues", [])
    if isinstance(issues, str):
        issues = [issues]
    if not isinstance(issues, list):
        issues = ["Invalid issues format"]
    issues = [str(x) for x in issues if str(x).strip()]

    verdict = str(report.get("verdict", "REVISE")).upper().strip()
    if verdict not in {"SAFE", "REVISE", "WARNING"}:
        verdict = "REVISE"

    return {
        "confidence_score": confidence_score,
        "hallucination_risk": hallucination_risk,
        "issues": issues,
        "verdict": verdict,
    }

class ConfidenceAgent(BaseAgent):
    async def evaluate(self, document: str):
        prompt = f"""You are a Confidence & Hallucination Detection Agent.

Evaluate the document below on:
1. Factual consistency
2. Unsupported claims
3. Vagueness
4. Overconfidence without evidence

Return ONLY valid JSON (no prose, no markdown, no code fences) with this schema:

{{
  "confidence_score": 0-100,
  "hallucination_risk": "LOW" | "MEDIUM" | "HIGH",
  "issues": ["..."],
  "verdict": "SAFE" | "REVISE" | "WARNING"
}}

Document:
----------------
{document}
----------------
"""

        raw = await self.think(prompt, purpose="validation")

        # Handle LLM routing sentinels explicitly (avoid misleading parse errors).
        raw_text = str(raw or "")
        if "__LLM_RATE_LIMITED__" in raw_text:
            return {
                "confidence_score": 40,
                "hallucination_risk": "HIGH",
                "issues": ["Confidence evaluation unavailable: __LLM_RATE_LIMITED__"],
                "verdict": "WARNING",
            }
        if "__LLM_UNAVAILABLE__" in raw_text:
            return {
                "confidence_score": 40,
                "hallucination_risk": "HIGH",
                "issues": ["Confidence evaluation unavailable: __LLM_UNAVAILABLE__"],
                "verdict": "WARNING",
            }

        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return _normalize_confidence_report(parsed)
            raise ValueError("Confidence evaluation was not a JSON object")
        except Exception:
            # Try again with common LLM formatting artifacts removed.
            cleaned = _strip_code_fences(raw_text)
            for candidate in (cleaned, _extract_json_object(cleaned)):
                if not candidate:
                    continue
                try:
                    parsed = json.loads(candidate)
                    if isinstance(parsed, dict):
                        return _normalize_confidence_report(parsed)
                except Exception:
                    pass

            # Safe fallback
            return {
                "confidence_score": 40,
                "hallucination_risk": "HIGH",
                "issues": [
                    "Confidence evaluation parse failed (model did not return valid JSON).",
                    f"Raw (truncated): {cleaned[:300]}" if isinstance(cleaned, str) else "Raw (truncated): <non-string>",
                ],
                "verdict": "WARNING"
            }

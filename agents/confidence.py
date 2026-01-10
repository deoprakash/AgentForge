from __future__ import annotations

import json
import re

from agents.base import BaseAgent


def _clamp_score(value, default: int = 40) -> int:
    try:
        score = int(value)
    except Exception:
        score = default
    return max(0, min(100, score))


def _extract_first_int(text: str) -> int | None:
    if not text:
        return None
    m = re.search(r"\b(\d{1,3})\b", text)
    if not m:
        return None
    return _clamp_score(m.group(1))


def _try_parse_score(text: str) -> int | None:
    """Accept either a bare integer or JSON like {"confidence_score": 72}."""
    if not text:
        return None

    t = text.strip()
    # Bare integer
    if t.isdigit():
        return _clamp_score(t)

    # JSON object (or JSON wrapped in code fences / prose)
    start = t.find("{")
    end = t.rfind("}")
    candidate = t[start : end + 1].strip() if start != -1 and end != -1 and end > start else None
    for attempt in (t, candidate):
        if not attempt:
            continue
        try:
            parsed = json.loads(attempt)
            if isinstance(parsed, dict) and "confidence_score" in parsed:
                return _clamp_score(parsed.get("confidence_score"))
        except Exception:
            continue

    # Fallback: first integer found
    return _extract_first_int(t)


class ConfidenceAgent(BaseAgent):
    """Evaluates confidence score AND detects hallucinations in documents.

    Returns both a confidence score and a hallucination risk assessment.
    """

    async def evaluate(self, document: str) -> dict:
        """Evaluate confidence score for a document."""
        prompt = f"""You are a confidence scoring agent.

Task: Return ONLY a confidence score from 0 to 100 for the document below.

Rules:
- Output must be either:
  - a single integer (preferred), OR
  - JSON: {{"confidence_score": <int 0-100>}}
- No other text.

Document:
----------------
{document}
----------------
"""

        raw = await self.think(prompt, purpose="validation")
        raw_text = str(raw or "").strip()

        # Handle router sentinels safely.
        if "__LLM_RATE_LIMITED__" in raw_text or "__LLM_UNAVAILABLE__" in raw_text:
            return {"confidence_score": 40, "source": "fallback", "raw": raw_text}

        score = _try_parse_score(raw_text)
        if score is None:
            score = 40
        return {"confidence_score": _clamp_score(score), "source": "llm"}

    async def detect_hallucinations(self, document: str) -> dict:
        """Detect hallucinations and unsupported claims in a document."""
        prompt = f"""You are a hallucination detection expert.

Analyze the document for hallucinations, unsupported claims, and factual errors.

Return JSON ONLY (NO other text):
{{
    "hallucination_risk": "LOW|MEDIUM|HIGH",
    "risk_score": <int 0-100>,
    "issues": ["issue1", "issue2"],
    "summary": "brief summary of risks"
}}

Examples:
- If document is factually sound: {{"hallucination_risk": "LOW", "risk_score": 10, "issues": [], "summary": "Document is factually grounded"}}
- If document has some concerns: {{"hallucination_risk": "MEDIUM", "risk_score": 45, "issues": ["unsupported claim about X"], "summary": "Minor unsupported claims found"}}
- If document has major issues: {{"hallucination_risk": "HIGH", "risk_score": 80, "issues": ["major factual error"], "summary": "Significant hallucinations detected"}}

Document:
----------------
{document}
----------------
"""

        raw = await self.think(prompt, purpose="validation")
        raw_text = str(raw or "").strip()

        # Handle router sentinels safely.
        if "__LLM_RATE_LIMITED__" in raw_text or "__LLM_UNAVAILABLE__" in raw_text:
            return {
                "hallucination_risk": "MEDIUM",
                "risk_score": 50,
                "issues": [],
                "summary": "Unable to assess (LLM unavailable)",
                "source": "fallback"
            }

        try:
            # Try multiple strategies to extract JSON
            # Strategy 1: Find JSON object in curly braces
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = raw_text[start:end+1]
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict) and "hallucination_risk" in parsed:
                        return {
                            "hallucination_risk": str(parsed.get("hallucination_risk", "MEDIUM")).upper(),
                            "risk_score": max(0, min(100, int(parsed.get("risk_score", 50)))),
                            "issues": list(parsed.get("issues", [])) or [],
                            "summary": str(parsed.get("summary", "No summary available")),
                            "source": "llm"
                        }
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"⚠️ Hallucination parsing error: {e}")
            pass

        # Fallback if parsing fails
        print(f"⚠️ Could not parse hallucination response. Raw: {raw_text[:100]}")
        return {
            "hallucination_risk": "MEDIUM",
            "risk_score": 50,
            "issues": [],
            "summary": "Unable to parse hallucination assessment",
            "source": "fallback"
        }

    async def evaluate_and_store(self, session_id: str, document: str) -> dict:
        """Run both confidence and hallucination checks, store results."""
        # Get confidence score
        confidence_result = await self.evaluate(document)
        
        # Get hallucination assessment
        hallucination_result = await self.detect_hallucinations(document)
        
        # Combine results
        combined_result = {
            "confidence_score": confidence_result.get("confidence_score", 40),
            "confidence_source": confidence_result.get("source", "unknown"),
            "hallucination_risk": hallucination_result.get("hallucination_risk", "MEDIUM"),
            "hallucination_risk_score": hallucination_result.get("risk_score", 50),
            "hallucination_issues": hallucination_result.get("issues", []),
            "hallucination_summary": hallucination_result.get("summary", ""),
        }
        
        try:
            await self.memory.save_actions(
                session_id,
                {
                    "type": "confidence_and_hallucination_report",
                    "confidence_score": int(combined_result.get("confidence_score", 40)),
                    "confidence_source": combined_result.get("confidence_source", "unknown"),
                    "hallucination_risk": combined_result.get("hallucination_risk", "MEDIUM"),
                    "hallucination_risk_score": combined_result.get("hallucination_risk_score", 50),
                    "hallucination_issues": combined_result.get("hallucination_issues", []),
                    "hallucination_summary": combined_result.get("hallucination_summary", ""),
                },
            )
        except Exception:
            # Avoid breaking the main flow if storage fails.
            pass
        return combined_result

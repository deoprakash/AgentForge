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
    """Computes a single confidence score for a document.

    No rewrite, no regeneration, no verdicts — just a score stored for later use.
    """

    async def evaluate(self, document: str) -> dict:
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

    async def evaluate_and_store(self, session_id: str, document: str) -> dict:
        result = await self.evaluate(document)
        try:
            await self.memory.save_actions(
                session_id,
                {
                    "type": "confidence_score",
                    "confidence_score": int(result.get("confidence_score", 40)),
                    "source": result.get("source", "unknown"),
                },
            )
        except Exception:
            # Avoid breaking the main flow if storage fails.
            pass
        return result

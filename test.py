"""Standalone Groq "should I respond?" tester.

This script is intentionally independent: it does NOT import any repo files.

It asks Groq to classify whether the assistant should respond to the user's
message, returning strict JSON. If it should respond, it also generates a
candidate response in the same call.

Env vars:
  - GROQ_API_KEY (required)
  - GROQ_MODEL (optional, default: llama-3.1-8b-instant)

Usage (PowerShell):
  python test.py
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from dotenv import load_dotenv

load_dotenv()

import httpx


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def _extract_json_object(text: str) -> dict[str, Any] | None:
	"""Best-effort extraction for cases where the model wraps JSON in prose."""
	text = (text or "").strip()
	if not text:
		return None

	try:
		data = json.loads(text)
		return data if isinstance(data, dict) else None
	except Exception:
		pass

	start = text.find("{")
	end = text.rfind("}")
	if start == -1 or end == -1 or end <= start:
		return None
	try:
		data = json.loads(text[start : end + 1])
		return data if isinstance(data, dict) else None
	except Exception:
		return None


def _as_decision(value: Any) -> str | None:
	if not isinstance(value, str):
		return None
	v = value.strip().lower()
	if v in {"respond", "response", "yes", "y", "true"}:
		return "RESPOND"
	if v in {"do_not_respond", "dont_respond", "do-not-respond", "ignore", "no", "n", "false"}:
		return "DO_NOT_RESPOND"
	return None


def call_groq_should_respond(*, api_key: str, model: str, user_message: str) -> dict[str, Any]:
	system = (
		"You are a gatekeeper. Decide whether an assistant should respond to the user's message. "
		"If the user is asking a question, requesting help, or expects an answer, respond. "
		"If the message is empty, spam, or clearly does not require a reply, do not respond. "
		"Return ONLY valid JSON with this schema:\n"
		"{\n"
		"  \"decision\": \"RESPOND\" | \"DO_NOT_RESPOND\",\n"
		"  \"reason\": string,\n"
		"  \"response\": string | null\n"
		"}\n"
		"Rules: decision must be exactly RESPOND or DO_NOT_RESPOND. If decision is DO_NOT_RESPOND, response must be null."
	)

	body = {
		"model": model,
		"temperature": 0,
		"max_tokens": 500,
		"messages": [
			{"role": "system", "content": system},
			{"role": "user", "content": user_message},
		],
	}

	headers = {
		"Authorization": f"Bearer {api_key}",
		"Content-Type": "application/json",
	}

	with httpx.Client(timeout=45) as client:
		resp = client.post(GROQ_API_URL, headers=headers, json=body)
		resp.raise_for_status()
		data = resp.json()

	content = (
		data.get("choices", [{}])[0]
		.get("message", {})
		.get("content", "")
	)
	parsed = _extract_json_object(content)
	if not parsed:
		return {
			"decision": "RESPOND",
			"reason": "Model did not return parseable JSON; defaulting to RESPOND.",
			"response": content.strip() or None,
			"raw": content,
		}

	decision = _as_decision(parsed.get("decision"))
	if not decision:
		decision = "RESPOND"
	parsed["decision"] = decision

	if decision == "DO_NOT_RESPOND":
		parsed["response"] = None
	else:
		resp_text = parsed.get("response")
		parsed["response"] = resp_text if isinstance(resp_text, str) and resp_text.strip() else None

	return parsed


def main() -> int:
	api_key = (os.getenv("GROQ_API_KEY") or "").strip()
	if not api_key:
		print("Missing GROQ_API_KEY env var.")
		return 2

	model = (os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant").strip()
	user_message = input("User message: ").strip()
	if not user_message:
		print("Empty message -> DO_NOT_RESPOND")
		return 0

	try:
		result = call_groq_should_respond(api_key=api_key, model=model, user_message=user_message)
	except httpx.HTTPStatusError as exc:
		status = getattr(exc.response, "status_code", None)
		text = getattr(exc.response, "text", "")
		print(f"Groq HTTP error: {status}\n{text}")
		return 1
	except Exception as exc:
		print(f"Groq call failed: {exc}")
		return 1

	decision = result.get("decision")
	reason = result.get("reason")
	response = result.get("response")

	print("\n--- decision ---")
	print(decision)
	if isinstance(reason, str) and reason.strip():
		print(f"Reason: {reason.strip()}")

	if decision == "RESPOND":
		print("\n--- response ---\n")
		print(response or "(no response provided)")

	return 0


if __name__ == "__main__":
	sys.exit(main())

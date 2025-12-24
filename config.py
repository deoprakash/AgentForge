import os
from dotenv import load_dotenv

load_dotenv()

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
DEFAULT_FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.com")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").strip().lower() in {"1", "true", "yes", "y"}
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").strip().lower()
LLM_GENERATION_PROVIDER = os.getenv("LLM_GENERATION_PROVIDER", LLM_PROVIDER).strip().lower()
LLM_VALIDATION_PROVIDER = os.getenv("LLM_VALIDATION_PROVIDER", LLM_PROVIDER).strip().lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Optional second key for failover.
GROQ_API_KEY_2 = os.getenv("GROQ_API_KEY_2")
# Optional: comma-separated list of Groq keys for rotation/failover.
# Example: GROQ_API_KEYS=key1,key2
_groq_keys_raw = os.getenv("GROQ_API_KEYS", "").strip()
GROQ_API_KEYS = [k.strip() for k in _groq_keys_raw.split(",") if k.strip()] if _groq_keys_raw else []

def _append_key(keys: list[str], key: str | None) -> list[str]:
	if key and key not in keys:
		keys.append(key)
	return keys

_append_key(GROQ_API_KEYS, GROQ_API_KEY)
_append_key(GROQ_API_KEYS, GROQ_API_KEY_2)

# Strategy for using multiple keys:
# - single: use first key only (strict, no extra calls)
# - failover_on_429: if first key gets HTTP 429, try next key once
GROQ_KEY_STRATEGY = os.getenv("GROQ_KEY_STRATEGY", "single").strip().lower()

# Optional pacing to reduce 429s (no retries, just spacing between calls).
# Example: GROQ_MIN_INTERVAL_SECONDS=1.5
try:
	GROQ_MIN_INTERVAL_SECONDS = float(os.getenv("GROQ_MIN_INTERVAL_SECONDS", "0"))
except Exception:
	GROQ_MIN_INTERVAL_SECONDS = 0.0
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")

_gemini_keys_raw = os.getenv("GEMINI_API_KEYS", "").strip()
GEMINI_API_KEYS = [k.strip() for k in _gemini_keys_raw.split(",") if k.strip()] if _gemini_keys_raw else []
_append_key(GEMINI_API_KEYS, GEMINI_API_KEY)
_append_key(GEMINI_API_KEYS, GEMINI_API_KEY_2)

# Ollama (local) configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

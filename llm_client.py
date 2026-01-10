import httpx
import asyncio
import time

from config import (
    GROQ_API_KEYS,
    GROQ_KEY_STRATEGY,
    GROQ_MIN_INTERVAL_SECONDS,
    GROQ_VALIDATION_MODEL,
    LLM_PROVIDER,
    LLM_GENERATION_PROVIDER,
    LLM_VALIDATION_PROVIDER,
)
try:
    from google.genai import Client as GeminiClient
except Exception:
    GeminiClient = None

# --------------------------------------------------
# Limit concurrent LLM calls (VERY IMPORTANT)
# --------------------------------------------------
LLM_SEMAPHORE = asyncio.Semaphore(1)  # strict to avoid rate limits

# Global Groq pacing (prevents bursts when multiple agents call sequentially)
_groq_pace_lock = asyncio.Lock()
_groq_last_request_at = 0.0


async def _pace_groq_requests() -> None:
    global _groq_last_request_at
    min_interval = float(GROQ_MIN_INTERVAL_SECONDS or 0.0)
    if min_interval <= 0:
        return

    async with _groq_pace_lock:
        now = time.monotonic()
        wait = (_groq_last_request_at + min_interval) - now
        if wait > 0:
            await asyncio.sleep(wait)
        _groq_last_request_at = time.monotonic()


# --------------------------------------------------
# Configure Gemini client (new SDK)
# --------------------------------------------------
# gemini_clients: list = []
# if GeminiClient:
#     for key in (GEMINI_API_KEYS or []):
#         try:
#             gemini_clients.append(GeminiClient(api_key=key))
#         except Exception:
#             pass


# --------------------------------------------------
# Groq call with retry
# --------------------------------------------------
async def call_groq(prompt: str, system: str = None, retries: int = 1, api_key: str | None = None, model: str = "llama-3.1-8b-instant"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    if not api_key:
        raise RuntimeError("Groq API key not configured")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages
    }

    for attempt in range(retries):
        try:
            await _pace_groq_requests()
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"⏳ Groq rate limited, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            raise


# --------------------------------------------------
# Gemini call (STABLE MODELS ONLY)
# --------------------------------------------------
async def call_gemini(prompt: str, model: str, client):
    if not client:
        raise RuntimeError("Gemini client not configured")

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=model,
        contents=prompt
    )
    return response.text


# --------------------------------------------------
# Unified LLM Router (Groq → Gemini Flash → Gemini Pro)
# --------------------------------------------------
def _select_provider(purpose: str) -> str:
    p = (purpose or "generation").strip().lower()
    if p in {"validation", "validate", "review"}:
        return (LLM_VALIDATION_PROVIDER or LLM_PROVIDER or "").strip().lower()
    return (LLM_GENERATION_PROVIDER or LLM_PROVIDER or "").strip().lower()


def _select_groq_keys_for_purpose(purpose: str) -> list[str]:
    if not GROQ_API_KEYS:
        return []
    p = (purpose or "generation").strip().lower()
    keys: list[str] = []

    # Primary separation: key1 for generation, key2 for validation (if present)
    if p in {"validation", "validate", "review"} and len(GROQ_API_KEYS) >= 2:
        primary_index = 1
        secondary_index = 0
    else:
        primary_index = 0
        secondary_index = 1

    keys.append(GROQ_API_KEYS[primary_index])

    # Optional failover (one extra attempt) while preserving the primary split.
    if GROQ_KEY_STRATEGY == "failover_on_429" and len(GROQ_API_KEYS) >= 2:
        keys.append(GROQ_API_KEYS[secondary_index])

    # de-dup while preserving order
    deduped: list[str] = []
    for k in keys:
        if k and k not in deduped:
            deduped.append(k)
    return deduped


def _select_gemini_client_for_purpose(purpose: str):
    if not gemini_clients:
        return None
    p = (purpose or "generation").strip().lower()
    # Separation: client1 for generation, client2 for validation (if present)
    if p in {"validation", "validate", "review"} and len(gemini_clients) >= 2:
        return gemini_clients[1]
    return gemini_clients[0]


def _select_gemini_clients_for_purpose(purpose: str):
    primary = _select_gemini_client_for_purpose(purpose)
    if not primary:
        return []
    if len(gemini_clients) < 2:
        return [primary]
    # Try the other client once if primary fails.
    secondary = gemini_clients[0] if primary is gemini_clients[1] else gemini_clients[1]
    return [primary, secondary]


async def call_llm(prompt: str, system: str = None, purpose: str = "generation"):
    provider = _select_provider(purpose)

    async def _call_with_provider(provider_name: str) -> str:
        name = (provider_name or "").strip().lower()

        if name == "groq":
            keys = _select_groq_keys_for_purpose(purpose)
            if not keys:
                return "__LLM_UNAVAILABLE__"
            # Select model based on purpose
            p = (purpose or "generation").strip().lower()
            model = GROQ_VALIDATION_MODEL if p in {"validation", "validate", "review"} else "llama-3.1-8b-instant"
            async with LLM_SEMAPHORE:
                last_status = None
                for i, key in enumerate(keys):
                    try:
                        return await call_groq(prompt, system, retries=1, api_key=key, model=model)
                    except httpx.HTTPStatusError as e:
                        status = getattr(e.response, "status_code", None)
                        last_status = status
                        if status == 429 and i < len(keys) - 1:
                            print("⚠️ Groq rate limited (429). Trying next key...")
                            continue
                        if status == 429:
                            print("⚠️ Groq rate limited (429).")
                            return "__LLM_RATE_LIMITED__"
                        print(f"⚠️ Groq HTTP error ({status}).")
                        return "__LLM_UNAVAILABLE__"
                    except Exception as e:
                        print(f"⚠️ Groq failed: {e}")
                        return "__LLM_UNAVAILABLE__"

                if last_status == 429:
                    return "__LLM_RATE_LIMITED__"
                return "__LLM_UNAVAILABLE__"

        if name == "gemini":
            clients = _select_gemini_clients_for_purpose(purpose)
            if not clients:
                return "__LLM_UNAVAILABLE__"
            async with LLM_SEMAPHORE:
                last_error = None
                for idx, client in enumerate(clients):
                    try:
                        return await call_gemini(prompt, "gemini-1.5-flash-latest", client)
                    except Exception as e:
                        last_error = e
                        try:
                            return await call_gemini(prompt, "gemini-2.5-pro", client)
                        except Exception as e2:
                            last_error = e2
                            if idx < len(clients) - 1:
                                print("⚠️ Gemini key failed. Trying next key...")
                                continue
                            break
                if last_error:
                    print(f"⚠️ Gemini failed: {last_error}")
                return "__LLM_UNAVAILABLE__"

        return "__LLM_UNAVAILABLE__"

    # Provider strictness:
    # - If user explicitly sets LLM_PROVIDER=groq, do exactly ONE Groq request.
    #   (No retries, no fallbacks, no artificial sleeps.)
    # Primary provider call
    result = await _call_with_provider(provider)

    # Validation fallback (non-recursive): if Gemini has no quota / is unavailable,
    # fall back to Groq validation key for smoother runs.
    p = (purpose or "generation").strip().lower()
    if p in {"validation", "validate", "review"} and result == "__LLM_UNAVAILABLE__" and provider != "groq":
        if GROQ_API_KEYS:
            return await _call_with_provider("groq")
    return result

    async with LLM_SEMAPHORE:

        # 1️⃣ Groq (fast, cheap)
        if GROQ_API_KEYS:
            try:
                keys = _select_groq_keys_for_purpose(purpose)
                if keys:
                    return await call_groq(prompt, system, retries=1, api_key=keys[0])
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")
            await asyncio.sleep(1)

        # 2️⃣ Gemini Flash (best free-tier stability)
        if gemini_clients:
            try:
                print("🔄 Trying Gemini Flash...")
                client = _select_gemini_client_for_purpose(purpose)
                return await call_gemini(prompt, "gemini-1.5-flash-latest", client)
            except Exception as e:
                print("⚠️ Gemini Flash quota exhausted or failed")
            await asyncio.sleep(1)

        # 3️⃣ Gemini Pro (best quality)
        if gemini_clients:
            try:
                print("🔄 Trying Gemini Pro...")
                client = _select_gemini_client_for_purpose(purpose)
                return await call_gemini(prompt, "gemini-2.5-pro", client)
            except Exception as e:
                print("⚠️ Gemini Pro quota exhausted or failed")
            await asyncio.sleep(1)

    # Absolute final fallback
    print("❌ All LLM providers exhausted.")
    return "__LLM_UNAVAILABLE__"

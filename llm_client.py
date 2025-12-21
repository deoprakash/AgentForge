import httpx
import asyncio
from config import GROQ_API_KEY, GEMINI_API_KEY
try:
    from google.genai import Client as GeminiClient
except Exception:
    GeminiClient = None

# --------------------------------------------------
# Limit concurrent LLM calls (VERY IMPORTANT)
# --------------------------------------------------
LLM_SEMAPHORE = asyncio.Semaphore(1)  # strict to avoid rate limits


# --------------------------------------------------
# Configure Gemini client (new SDK)
# --------------------------------------------------
gemini_client = None
if GEMINI_API_KEY and GeminiClient:
    gemini_client = GeminiClient(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# Groq call with retry
# --------------------------------------------------
async def call_groq(prompt: str, system: str = None, retries: int = 2):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
    }

    for attempt in range(retries):
        try:
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
async def call_gemini(prompt: str, model: str):
    if not gemini_client:
        raise RuntimeError("Gemini client not configured")

    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model=model,
        contents=prompt
    )
    return response.text


# --------------------------------------------------
# Ollama (LOCAL LLM fallback)
# --------------------------------------------------
async def call_ollama(prompt: str):
    """
    Local LLM fallback using Ollama
    Requires: ollama running on localhost:11434
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
    except Exception as e:
        print(f"⚠️ Ollama failed: {e}")
        raise


# --------------------------------------------------
# Unified LLM Router (Groq → Gemini Flash → Gemini Pro → Ollama)
# --------------------------------------------------
async def call_llm(prompt: str, system: str = None):
    # aggressive spacing to avoid provider throttling
    await asyncio.sleep(2.5)

    async with LLM_SEMAPHORE:

        # 1️⃣ Groq (fast, cheap)
        if GROQ_API_KEY:
            try:
                return await call_groq(prompt, system, retries=2)
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")
            await asyncio.sleep(1)

        # 2️⃣ Gemini Flash (best free-tier stability)
        if gemini_client:
            try:
                print("🔄 Trying Gemini Flash...")
                return await call_gemini(prompt, "gemini-1.5-flash-latest")
            except Exception as e:
                print("⚠️ Gemini Flash quota exhausted or failed")
            await asyncio.sleep(1)

        # 3️⃣ Gemini Pro (best quality)
        if gemini_client:
            try:
                print("🔄 Trying Gemini Pro...")
                return await call_gemini(prompt, "gemini-2.5-pro")
            except Exception as e:
                print("⚠️ Gemini Pro quota exhausted or failed")
            await asyncio.sleep(1)

        # 4️⃣ Ollama (LOCAL, NO QUOTA)
        try:
            print("🧠 Using local Ollama fallback")
            return await call_ollama(prompt)
        except Exception:
            pass

    # 5️⃣ Absolute final fallback
    print("❌ All LLM providers exhausted.")
    return "__LLM_UNAVAILABLE__"

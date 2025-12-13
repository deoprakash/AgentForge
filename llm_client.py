import httpx
from config import LLM_PROVIDER, GROQ_API_KEY

async def call_llm(prompt: str, system: str = None):
    if LLM_PROVIDER == "groqai":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        body = {
            "model": "llama-3.1-8b-instant",
            "messages": []
        }

        if system:
            body["messages"].append({"role": "system", "content":system})
        
        body["messages"].append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=body, headers=headers)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        
    return f"[MOCK LLM] {prompt[:200]}"

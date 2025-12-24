# AgentForge
AgentForge is a multi-agent AI system that autonomously plans, generates, stores, and delivers business and research documents using long-term memory.

## Setup (Groq)

1) Create a `.env` file (already supported via `python-dotenv`) and set:

- `LLM_PROVIDER=groq`
- `GROQ_API_KEY=...` (single key)

Optional (multiple keys for smoother runs):

- `GROQ_API_KEYS=key1,key2`
- `GROQ_KEY_STRATEGY=failover_on_429` (tries key2 once if key1 hits 429)

Optional (reduce 429s by pacing requests):

- `GROQ_MIN_INTERVAL_SECONDS=1.5`

2) Install deps:

- `pip install -r requirements.txt`

3) Run the API:

- `python server.py`

Health check:

- `GET http://localhost:8000/health`

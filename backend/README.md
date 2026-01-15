# Intellixa — Backend

This folder contains the FastAPI backend for Intellixa (multi-agent orchestration).

## Requirements

- Python 3.10+
- MongoDB (or run in-memory mode)
- Recommended: create a virtual environment

## Setup

1. Create and activate a virtual env (optional but recommended):

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
# or if using pyproject.toml and poetry/pip-tools, install accordingly
```

3. Environment variables

Create a `.env` (or export env vars) with the following keys:

- `APP_HOST` (default `0.0.0.0`)
- `APP_PORT` (default `8000`)
- `MONGO_URI` (MongoDB connection string) — required if you want persistent storage

Example `.env`:

```
APP_HOST=0.0.0.0
APP_PORT=8000
MONGO_URI=mongodb://localhost:27017
```

Note: If `MONGO_URI` is not set or `motor` is not installed, the app will fall back to an in-memory store.

## Run

You can run the backend directly (project includes a `server.py` entry) or with Uvicorn:

```bash
# simple: run with python
python server.py

# or with uvicorn (recommended for development)
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Check console logs for a message like:

```
[MemoryStore] MongoDB connected: <your-mongo-uri>
# or
[MemoryStore] MongoDB NOT connected. Using in-memory store.
```

This confirms whether MongoDB is being used.

## Key Files

- `server.py` — FastAPI app and HTTP endpoints
- `memory.py` — Persistence layer (MongoDB via Motor or in-memory fallback)
- `orchestrator.py` / `orchestrator_langgraph.py` — Core orchestration logic
- `utils.py` — helpers and serializers
- `agents/` — agent implementations

## API Endpoints

- `GET /health` — health check
- `POST /run` — start an orchestration run
  - Body: JSON with `goal` (string) and optional `email` or `command`
  - Returns: run result object; includes `session_id` when stored

- `POST /run/legacy` — legacy run endpoint (goal + email)

- `GET /session/{session_id}` — fetch stored session and latest document
  - Returns session metadata, `final` document, `plan`, and `handoff` information

- `POST /approve` — human-in-the-loop approval endpoint
  - Body: `{ session_id: string, decision: string }`

## Example: fetch a final draft

```bash
curl http://localhost:8000/session/<session_id>
```

If the backend returns `404`, ensure the `session_id` exists in MongoDB (see `document` collection) and that `MONGO_URI` is correct.

## Debugging tips

- Watch backend logs — the service prints debug lines when locating sessions and when Mongo is connected.
- If you see `Session not found` in logs but the ID exists in Mongo, verify the `session_id` stored in the DB matches what the frontend sends (sometimes one field is `_id` ObjectId while code looks for `session_id`). The backend attempts both ObjectId lookups and `session_id` string matches.
- For local development without MongoDB, the in-memory store will be used — data will not persist between restarts.

## Tests / Development

- You can run `server.py` and exercise endpoints via Postman or curl.
- When changing DB-related code, restart the server to pick up changes.

---

If you want, I can also:
- Add example `docker-compose.yml` to start Mongo + backend
- Add small scripts to seed the `document` collection for testing


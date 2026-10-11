# How it works

A plain-English note appended after each milestone.

## M0: Scaffold

- The **backend** is a FastAPI app. `backend/app/main.py` builds it: it reads settings (`config.py`), registers one error format (`errors.py`), connects to MongoDB (`database.py`) and mounts the routers under `/api`.
- `config.py` reads `backend/.env`. If `AUTH_MODE=dev` is set anywhere except `ENV=development`, the server refuses to start.
- `deps.py` has `get_current_user`, which every protected route depends on. In dev mode it trusts the `X-Dev-User` header; the Firebase branch comes in M1.
- `routers/health.py` reports the status and which AI providers are configured. `routers/auth.py` (`GET /api/me`) creates or updates the user document with one atomic upsert.
- `ai/llm_client.py` is the only door to LLMs. It tries each provider in `LLM_CHAIN`, checks the JSON against a Pydantic model, retries once on bad JSON, then falls back. `ai/speech/stt_client.py` does the same for speech to text. Only the offline `mock` providers exist so far.
- The **frontend** is React + Vite. `App.tsx` lists every route. `lib/api.ts` is the one fetch wrapper: it adds the login header and turns server errors into readable messages. Vite forwards `/api` calls to port 8000, so the browser only ever talks to one address.
- Login is a stub. `store/authStore.ts` remembers a dev user name, and `LoginPage.tsx` sets it. M1 swaps in Firebase.
- All styling is in `frontend/src/styles/globals.css`.

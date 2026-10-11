# Decisions log

One line per decision made during the build where the brief left a choice open.

## M0
- **Python 3.14** (the default `py` on the dev laptop). Every dependency, including faster-whisper's native parts (ctranslate2, onnxruntime, av), ships Windows wheels for 3.14, so no C compiler is needed. The newest `av` needs 3.12 or later.
- **httpx2 instead of httpx.** Starlette 1.x (under FastAPI) deprecates `httpx` for its TestClient in favour of `httpx2`, the Pydantic-maintained successor. LLM calls will use it too, so there is one HTTP library.
- **`user_id` = Firebase uid** (dev mode: `dev-<name>`). Every document stores it directly, so no user lookup is needed on each request.
- **Two env examples, no root copy:** `backend/.env.example` and `frontend/.env.example`. One copy each, so they cannot drift apart.
- **Backend starts even when MongoDB is down.** It logs a clear error, `/api/health` shows `database: unreachable`, database routes return 503, and the next request tries to reconnect.
- **`/api/health` has an extra `database` field** so a missing database is visible at a glance.
- **Lint uses oxlint**, the current create-vite default, instead of ESLint.
- **React Router v8** via the single `react-router` package.
- **The Firebase JS SDK, google-auth and requests are installed in M0,** so the parallel auth branch (AGENTS.md) never needs to edit `package.json` or `requirements.txt`.
- **Model IDs** (checked in the official docs, Oct 2026). Groq: fast `openai/gpt-oss-20b`, report `openai/gpt-oss-120b`, STT `whisper-large-v3-turbo`. Gemini: fast `gemini-3.5-flash-lite`, report `gemini-3.8-flash` (both have a free tier).
- **Groq structured output:** both gpt-oss models support strict `json_schema` output on Groq, so M3 uses strict schemas there. Pydantic validation and one retry still apply.
- **Dev sign-in in the frontend:** the name is kept in localStorage and sent as `X-Dev-User` whenever there is no Firebase token. The backend ignores it unless `AUTH_MODE=dev` and `ENV=development`.
- **Frontend routes:** `/login`, `/`, `/new`, `/interviews/:id/check`, `/interviews/:id`, `/reports/:id`, `/diagnostics`.
- **Backend tests use a small in-memory fake database,** so `pytest` needs no running MongoDB.
- **The dev auth tests are named `test_dev_auth.py`** so they do not collide with `test_auth.py`, which the parallel auth branch owns.

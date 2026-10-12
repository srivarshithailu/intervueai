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

## M1: Firebase sign-in

- **Signing in (browser):** `lib/firebase.ts` is the only file that imports the Firebase SDK. It sets Firebase up from `frontend/.env.local` and offers Google sign-in, email sign-in and sign-up, password reset and sign-out. Firebase keeps the session across page refreshes on its own.
- **Which sign-in screen:** at startup, `store/authStore.ts` asks `/api/health` which `auth_mode` the backend uses. For `firebase` it listens to Firebase's sign-in state and gives `lib/api.ts` a token getter, so every API call carries `Authorization: Bearer <ID token>`. For `dev` it keeps the old dev sign-in.
- **Pages:** `LoginPage.tsx` shows `FirebaseSignInForm` or `DevSignInForm` and moves on once a user exists. `ProtectedRoute.tsx` shows "Checking sign-in..." while loading and sends signed-out visitors to `/login`.
- **Checking the token (server):** `deps.py` takes the token from the header and calls `firebase_auth.verify_id_token` in a background thread. google-auth checks the signature, expiry and project. Our code also checks the issuer, the user id and the sign-in time, which google-auth skips. Google's public keys are cached, so only the first check downloads them.
- **Result:** a valid token becomes `CurrentUser(uid, email, name)`. Anything else is a 401 with a plain message, or a 503 if Google's keys cannot be downloaded. `/api/me` then upserts the `users` document keyed by that uid.
- **Isolation:** the user id comes only from the verified token, never from the request body or other headers, so one user can never act as another.

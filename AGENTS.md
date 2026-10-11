# IntervueAI: instructions for Antigravity (authentication task only)

You are working on ONE slice of a larger project: **login and authentication**. Another coding agent (Claude Code) is building the rest of the app in a different folder at the same time. Stay inside your slice so the two branches merge cleanly.

The full project brief is `CLAUDE.md` in this repo. Read its sections "What IntervueAI is", "Style rules for the v0 UI" and "Credentials and fallbacks", plus `docs/spec/architecture.md` (file layout), for context. Do not edit `CLAUDE.md`.

## Project in one paragraph
IntervueAI is an adaptive mock interview web app (React + TypeScript + Vite frontend, FastAPI + MongoDB backend). Candidates sign in, upload a resume, take a voice interview, and get a report. Login is **Firebase Authentication** (Google sign-in + email/password). The browser gets a Firebase ID token; every API call sends it as `Authorization: Bearer <token>`; the backend verifies it.

## Your task
Replace the auth stubs with a working Firebase login, on this branch only.

### Files you may create or edit
Frontend:
- `frontend/src/lib/firebase.ts`: initialise Firebase from `VITE_FIREBASE_*` env vars; export `auth` and helper functions (`signInWithGoogle`, `signInWithEmail`, `signUpWithEmail`, `signOutUser`).
- `frontend/src/lib/api.ts`: only wire the existing token getter so every request sends a fresh ID token (`auth.currentUser.getIdToken()`). Do not change anything else in this file.
- `frontend/src/store/authStore.ts`: Zustand store: `user`, `loading`, `error`; listens to `onAuthStateChanged`.
- `frontend/src/pages/LoginPage.tsx`: the login and sign-up screen.
- `frontend/src/components/ProtectedRoute.tsx`: redirects to `/login` when signed out, shows a skeleton while auth state loads.
- `frontend/.env.example`: the four `VITE_FIREBASE_*` variables with comments.
- `frontend/src/**/*.test.ts(x)`: tests for your files only.

Backend:
- `backend/app/deps.py`: fill in the `firebase` branch of `get_current_user`. Keep the existing `dev` branch.
- `backend/app/routers/auth.py`: `GET /api/me` (create the user document on first call, return it).
- `backend/tests/test_auth.py`

**Do not touch** any other file (`App.tsx`, `main.py`, `ai/`, `services/`, other pages, `CLAUDE.md`, other tests). If you think another file needs a change, write it in your final report instead.

## Requirements
Login page:
- Google button, email/password form, switch between "Sign in" and "Create account", "Forgot password" (Firebase password reset email).
- Friendly error messages for the common cases (wrong password, email in use, weak password, popup closed, network error). Never show raw Firebase error codes.
- Loading states on buttons, keyboard accessible, labels on inputs.
- Look: minimal black and white, plain HTML-style form in a centered column, system font stack, no animation, no icons, no extra UI libraries. Follow the "Style rules for the v0 UI" section of `CLAUDE.md` and use only class names from `styles/globals.css` (add classes there only if needed).

Auth state:
- Persist the session across refresh (Firebase default).
- Sign-out button helper available to other components via the store.
- After sign-in go to `/` (the dashboard route already exists).

Backend verification:
- `AUTH_MODE=firebase`: verify the ID token against `FIREBASE_PROJECT_ID` (check the current Firebase docs; prefer a method that needs no service-account file, such as Google's `google-auth` verify function for Firebase tokens). Reject expired, wrong-audience or malformed tokens with 401 and body `{"error": {"code": "unauthorized", "message": "..."}}`.
- `AUTH_MODE=dev`: accept an `X-Dev-User` header **only when `ENV=development`**. In any other environment dev mode must fail closed (refuse to start or return 401). Keep this behaviour; do not weaken it.
- `GET /api/me`: upsert a document in the `users` collection keyed by `firebase_uid`, with `email`, `name`, `created_at`. Calling it twice must not create duplicates.

## Rules
- Do not guess library versions or API names; check the current official docs for the Firebase JS SDK and for token verification.
- No secrets in git. Real keys go in `.env` / `frontend/.env.local`, which are ignored.
- Simple, readable code. Every new file starts with a 1-2 line comment saying what it is for. Comment the why, not the what. Four students will learn this code, so avoid clever tricks.
- Explain any new library in one sentence.
- Do not ask questions unless you are blocked on a missing credential. If Firebase config is missing, build everything against `AUTH_MODE=dev` and tests with a mocked verifier, and say so in your report.

## Tests required
- No token -> 401. Malformed token -> 401. Valid token (mocked verifier) -> 200 and a user document.
- `/api/me` called twice -> one user document.
- Dev mode with `ENV=production` -> refused.
- Frontend: the store's sign-in/out state transitions with a mocked Firebase module.

## Done means
- `pytest` passes for the auth tests; `npm run build` and `npm run lint` pass.
- The login page works end to end with real Firebase config (if provided) and in dev mode.
- Commit on the current branch with clear messages. **Do not merge and do not push.**
- Final report: what you built, how to run it, how to configure Firebase (Google and Email/Password providers enabled, `localhost` in authorized domains), anything skipped, and a 5-line "how it works" note for the students.

# API contract

The REST API as built so far. Planned endpoints are listed in `docs/spec/api_and_pages.md`; each one moves here when it is built.

All paths start with `/api`. Bodies are JSON. The frontend calls them through the Vite proxy (`/api` -> `http://localhost:8000`).

## Authentication

Every endpoint except `/health` needs a signed-in user.

| `AUTH_MODE` | What the client sends | Notes |
|---|---|---|
| `firebase` | `Authorization: Bearer <Firebase ID token>` | Needs `FIREBASE_PROJECT_ID` (the server will not start without it). `X-Dev-User` is ignored. |
| `dev` | `X-Dev-User: <name>` (1-64 chars: letters, digits, `_ . @ -`) | **Only when `ENV=development`.** The server will not start with `AUTH_MODE=dev` in any other environment, and each request checks this again. The user id becomes `dev-<name>`. |

The frontend reads `auth_mode` from `GET /api/health` and shows the matching sign-in screen.

**Firebase token checks**, done in `app/firebase_auth.py`:
- The signature must match one of Google's public keys. The keys are cached for as long as Google's `Cache-Control` header allows.
- `exp` and `iat` must be valid, allowing 10 seconds of clock skew.
- `aud` must equal `FIREBASE_PROJECT_ID`.
- `iss` must equal `https://securetoken.google.com/<FIREBASE_PROJECT_ID>`.
- `sub` (the user id) must be non-empty and at most 128 characters.
- `auth_time` must not be in the future.
- Tokens longer than 4096 characters are rejected without being parsed.

Each failure returns 401 with a plain message: "Please sign in.", "Your sign-in has expired. Please sign in again.", "This sign-in is for a different Firebase project than the server expects." or "Invalid sign-in token."

## Errors

Every error has the same shape:

```json
{"error": {"code": "unauthorized", "message": "Plain-English explanation"}}
```

| Status | `code` | When |
|---|---|---|
| 401 | `unauthorized` | No login, or the login is invalid |
| 404 | `not_found` | Unknown path or record |
| 422 | `invalid_input` | Body or parameters fail validation |
| 503 | `database_unavailable` | MongoDB cannot be reached |
| 503 | `auth_unavailable` | Google's public keys cannot be downloaded, so Firebase tokens cannot be checked |

Later milestones add 413, 415, 429 and other 503 codes.

## Endpoints

### `GET /api/health`
No login needed.

Response 200:
```json
{"status": "ok", "llm_chain": ["mock"], "stt_chain": ["mock"], "auth_mode": "dev", "database": "connected"}
```
`database` is `"connected"` or `"unreachable"`.

### `GET /api/me`
Returns the signed-in user. The first call creates the `users` document. Calling it again updates name and email and never creates a duplicate.

Response 200:
```json
{"user_id": "dev-asha", "email": "asha@dev.local", "name": "asha", "created_at": "2026-10-11T10:31:00Z"}
```
`user_id` is the Firebase uid (`sub` in the token). Every stored document is tagged with this value. `email` and `name` come from the token and may be empty; for example, email sign-up sets no name.

Errors: 401, 503 (`database_unavailable` or `auth_unavailable`).

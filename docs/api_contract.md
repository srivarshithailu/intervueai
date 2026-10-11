# API contract

The REST API as built so far. Planned endpoints are listed in `docs/spec/api_and_pages.md`; each one moves here when it is built.

All paths start with `/api`. Bodies are JSON. The frontend calls them through the Vite proxy (`/api` -> `http://localhost:8000`).

## Authentication

Every endpoint except `/health` needs a signed-in user.

| `AUTH_MODE` | What the client sends | Notes |
|---|---|---|
| `firebase` | `Authorization: Bearer <Firebase ID token>` | Verification is built in M1. Until then every request gets 401. |
| `dev` | `X-Dev-User: <name>` (1-64 chars: letters, digits, `_ . @ -`) | **Only when `ENV=development`.** The server will not start with `AUTH_MODE=dev` in any other environment, and each request checks this again. The user id becomes `dev-<name>`. |

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
`user_id` is the Firebase uid. Every stored document is tagged with this value.

Errors: 401, 503.

# IntervueAI

**IntervueAI: An Intelligent Adaptive Mock Interview and Multimodal Performance Assessment System.**

An adaptive mock interview web app. Sign in, upload a resume, pick a role, level and interview type (Technical or HR), and have a spoken interview with an AI interviewer. Each next question depends on how the last answer scored. A report follows at the end.

Status: **v0 in progress** (milestone M0, the scaffold). The build plan is in `CLAUDE.md`, and the specs are in `docs/spec/`.

> **Free-tier data warning.** Google may use free-tier Gemini prompts and responses to improve its products, and other free tiers may log prompts. **For demos, use only the fake sample resume** (`samples/sample_resume.pdf`, added in M2), never a real person's resume.

## What you need

- Windows with Chrome or Edge
- Python 3.11 or newer (developed on 3.14): `py --version`
- Node.js 20 or newer (developed on 24): `node --version`
- MongoDB: either Docker Desktop, a local MongoDB Community Server, or a free MongoDB Atlas cluster (see below)

No API keys are needed to start. The defaults use offline `mock` AI providers and a dev login.

## Run it (PowerShell)

### 1. Backend (terminal 1)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

If PowerShell says running scripts is disabled, allow it for this window only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Check it at <http://localhost:8000/api/health>.

### 2. Frontend (terminal 2)

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open <http://localhost:5173>. Sign in with any dev user name (for example `asha`).

### 3. MongoDB (pick one)

- **Docker:** from the repo root, run `docker compose up -d mongo`. The default `MONGODB_URI=mongodb://localhost:27017` works as is.
- **MongoDB Community Server (no Docker):** install the free Windows MSI from mongodb.com and run it as a service. The default URI works.
- **MongoDB Atlas (free cloud):**
  1. Sign up at <https://www.mongodb.com/cloud/atlas> and create a **free** cluster.
  2. Under *Database Access*, add a database user with a password.
  3. Under *Network Access*, add your current IP address.
  4. Click *Connect* > *Drivers* and copy the `mongodb+srv://...` string. Put your password into it.
  5. Set `MONGODB_URI=` to that string in `backend/.env`.

The backend still starts without a database. `/api/health` then shows `"database": "unreachable"`, and the log says what to fix. Once MongoDB is up, the next request reconnects, with no restart needed.

## Tests and checks

Backend (in `backend`, with the venv active):

```powershell
pytest
```

Frontend (in `frontend`):

```powershell
npm test
npm run lint
npm run build
```

None of these needs keys, a network connection or MongoDB.

## Getting the free keys (when you are ready to leave mock mode)

Keys go in `backend/.env` and `frontend/.env.local`, which git ignores. Never commit them.

### Firebase (login, used from M1)
1. Go to <https://console.firebase.google.com> > *Add project* (Google Analytics is not needed).
2. *Build* > *Authentication* > *Get started* > *Sign-in method*: enable **Google** and **Email/Password**.
3. *Authentication* > *Settings* > *Authorized domains*: make sure `localhost` is listed (it is by default).
4. *Project settings* > *General* > *Your apps* > add a **Web** app. Copy `apiKey`, `authDomain`, `projectId` and `appId` into the `VITE_FIREBASE_*` lines of `frontend/.env.local`.
5. In `backend/.env`, set `FIREBASE_PROJECT_ID` to the same project id and `AUTH_MODE=firebase`.

### Groq (fast LLM and Whisper speech to text)
1. Sign in at <https://console.groq.com>, open *API Keys* and create one.
2. Set `GROQ_API_KEY=` in `backend/.env`. The model ids are already filled in.

### Gemini (second LLM and final report)
1. Sign in at <https://aistudio.google.com>, click *Get API key* and create one.
2. Set `GEMINI_API_KEY=` in `backend/.env`.

Then switch the chains, for example `LLM_CHAIN=groq,gemini`, `LLM_CHAIN_REPORT=gemini,groq` and `STT_CHAIN=groq,local`. Real providers are wired in M3 (LLM) and M4 (speech).

## Privacy

The resume file is never stored, only the extracted profile. Audio is never stored. Video never leaves the browser. Every database query is filtered by the signed-in user.

## Project layout

See `docs/spec/architecture.md`. Other docs: `docs/api_contract.md` (API as built), `docs/how_it_works.md` (one note per milestone), `docs/decisions.md` (choices made during the build).

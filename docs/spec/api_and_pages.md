# REST API and frontend pages

Spec file for milestones M0, M1, M3 and M8. The rules in CLAUDE.md always apply.

## 10. REST API (document all of it in `docs/api_contract.md`)

All under `/api`, JSON, `Authorization: Bearer <Firebase ID token>` except health.

- `GET /health` -> `{status, llm_chain, stt_chain, auth_mode}`
- `GET /me` -> current user (create on first call)
- `POST /resume` (multipart `file`) -> `{resume_id, profile}`
- `POST /interviews` `{resume_id, role, level, type, max_questions?}` -> `{interview_id, first_question: {text, topic, kind, index}}`
- `GET /interviews/{id}` -> resumable state without scores: `{status, question_index, max_questions, current_question, ...}`
- `POST /interviews/{id}/transcribe` (multipart `audio` WAV, `seq`, `duration_ms`, optional `provider` override honoured only for the Diagnostics page) -> `{seq, text, provider, ms}`
- `POST /interviews/{id}/answer` `{question_index, answer_text, input_mode: "voice"|"text", speaking_seconds?, response_latency_seconds?, segments?: [{seq, duration_ms}], client_timings?}` -> `{next_question: {text, topic, kind, index} | null, finished: bool}`
- `POST /interviews/{id}/finish` `{camera_metrics?}` -> `{report_id}` (idempotent; also usable to end early)
- `GET /reports` -> list (id, role, type, level, overall score, date)
- `GET /reports/{id}` -> full report
- `GET /diagnostics/providers` -> runs a tiny test through each configured LLM and STT provider and returns status and latency (rate-limited per user)
- `DELETE /me/data` -> deletes the user's resumes, interviews and reports

Errors: `{error: {code, message}}` with 401, 404, 413, 415, 422, 429, 503. Rate-limit expensive endpoints per user (simple in-memory limiter). Run blocking work (PyMuPDF, faster-whisper) with `asyncio.to_thread`.

## 11. Frontend (v0: minimal, black and white)

**Style rules** (put them in `styles/globals.css`, nothing else styles the app):
- White background, black text, grays allowed for secondary text. **No other colors**, no icons, no images, no animations, no shadows, no external fonts (system font stack).
- Centered column, max width about 720 px, comfortable line height and spacing.
- Buttons and inputs: 1 px black border, square corners; hover inverts to black background with white text; visible 2 px focus outline.
- Warnings and notices: bordered box with bold text. State is conveyed by words and borders, not color.
- Semantic HTML (`h1`, `label`, `table`, `button`, `fieldset`), labelled controls, keyboard accessible. No inline styles; class names only. This keeps a later re-skin to a CSS and markup change, not a rewrite.
- Report charts: plain `<table>` and simple bar rows made from `<div>` widths. No chart library.

**Pages**
1. **Login:** Google button, email/password form, switch between sign in and create account, "forgot password", friendly error text (never raw Firebase codes).
2. **Home:** "Start new interview", a table of past reports (date, role, type, level, score), sign out, "Delete my data" with confirmation, link to Diagnostics.
3. **New interview:** upload resume (shows the parsed profile as plain lists for the user to confirm), role (text input with suggestions), level, type (radio buttons), start.
4. **Check (before the interview):** headphone advice; mic test with a text level indicator and a "say something" check that VAD detects speech; camera preview with "face detected: yes/no"; TTS test button (and Kokoro warm-up progress as text); browser check (Chrome or Edge recommended); consent text: "Your video and audio are not stored. Face detection runs on your device. Audio clips are sent to a speech-to-text service for transcription and discarded." If mic or camera is denied, say so plainly and continue in text mode / without camera.
5. **Interview:** shows "Question 3 of 8", the question text, status line in words ("Interviewer speaking", "Your turn: listening", "Heard: ...", "Submitting in 2 s", "Thinking"), the running transcript of the current answer, the camera notice area, buttons: Submit answer, Repeat question, Skip speech, Type instead, End interview (with confirm). A small camera preview. Refreshing the page resumes at the current question.
6. **Report:** overall score, dimension table, communication table, camera table, summary, strengths, improvements, next steps, per-question list (question, transcript, scores, feedback), back to home.
7. **Diagnostics:** plain-text test panel (spec in `vision_diagnostics.md`).

Robustness: a visible banner when offline; retry with backoff for transient API errors using the same payload (idempotent answer endpoint); handle tab hidden/visible and mic device change; clear messages for every failure.

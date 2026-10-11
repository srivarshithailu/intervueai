# Voice pipeline

Spec file for milestones M4, M5 and M7. The rules in CLAUDE.md always apply.

## 6. The voice pipeline (most important part; make it excellent)

Goal: after the candidate finishes speaking, the next question starts playing as soon as possible, and nothing feels broken. Design target (measure it, do not promise it): end of answer to first audio of the next question in about 3-4 seconds.

**Capture (browser)**
- `getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } })`. Recommend headphones in the Check page.
- Silero VAD (`@ricky0123/vad-web`) runs continuously while it is the candidate's turn and yields one audio segment per stretch of speech. Encode each segment to 16 kHz mono 16-bit WAV (`wav.ts`). Force-split any segment longer than 45 s. Ignore segments under 0.4 s.
- **The mic is gated while the interviewer speaks** (VAD paused) so the app never transcribes itself. A "Skip" button stops the interviewer's speech. Barge-in is out of scope.

**Pipelined transcription**
- Each segment is sent immediately to `POST /api/interviews/{id}/transcribe` while the candidate may still be speaking or thinking. The client keeps the texts in order by `seq`. By the time the answer ends, most of the transcript is already done.

**End-of-answer detection (`turnEnd.ts`, pure function, unit-tested)**
- After a segment ends, wait `endSilenceMs` before submitting; if new speech starts in the window, the same answer continues.
- Adaptive wait using the transcript text of the last segment: ends with `. ? !` -> 1200 ms; ends mid-sentence or with a trailing conjunction or filler (and, so, because, but, um, uh, like, or, then) -> 3000 ms; otherwise 2000 ms. All values live in `lib/settings.ts`.
- Show plain text "Submitting in 2 s. Speak to continue." and a "Submit answer now" button (also the Enter key). Always provide "Type instead" and "Repeat question".

**Speech to text (server, `ai/speech/`)**
- Chain from `STT_CHAIN` (for example `groq,local`). Groq: Whisper large-v3-turbo through its OpenAI-compatible audio transcription endpoint (confirm in docs), `language=en`, `temperature=0`. Local fallback: faster-whisper (`LOCAL_WHISPER_MODEL`, default `small.en`) run with `asyncio.to_thread`, model loaded once and cached. Install faster-whisper as an optional extra.
- Send a Whisper `prompt` that (a) contains natural fillers so Whisper keeps them ("Umm, so, uh, I think, like, you know, basically...") and (b) lists the candidate's skills, tools and project names from the resume as vocabulary hints. Keep the prompt short.
- Reject hallucinations on near-silence: use the response's no-speech indicators when available; drop empty or known filler outputs such as "Thank you." or "Thanks for watching." on very short segments.
- Per-provider timeout, retry once, then fall to the next provider (circuit breaker: skip a failing provider for 60 s).
- Audio is processed in memory and discarded. Segment size limit `MAX_SEGMENT_MB` (default 3). Never write audio to disk (if a temp file is unavoidable, delete it in `finally`).

**Text to speech (client, `voice/tts/`)**
- One interface: `speak(text, onFirstAudio?, onEnd?)`, `cancel()`, `warmup()`.
- Chain: `kokoroTts` (kokoro-js in a Web Worker; requires an actual WebGPU adapter: request it explicitly, since `navigator.gpu` can exist without a usable adapter) -> `browserTts` (speech synthesis; voices load asynchronously; prefer natural/online English voices, then other English voices). If Kokoro is not ready within the question's display time, fall back for that question without blocking.
- Speak the question sentence by sentence (queue) so the first sentence starts quickly.
- Warm up Kokoro in the Check page (download is cached after the first run; show progress as text). Store the chosen voice in localStorage.
- Never block the interview on TTS failure: show the question text always.

**Timing instrumentation (required)**
- Record per turn: `vad_end -> transcribe_done`, `answer_submit -> llm_done`, `question_received -> tts_first_audio`, plus provider names used. Store in `turns[].timings` and show a small plain-text timing table on the Diagnostics page. This is how we will prove and tune speed.

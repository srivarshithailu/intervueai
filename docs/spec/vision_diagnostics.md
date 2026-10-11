# Camera presence and Diagnostics page

Spec file for milestones M6 and M7. The rules in CLAUDE.md always apply.

## 12. Camera presence

- `presenceTracker.ts` is pure logic (no DOM) and unit-tested. Input: stream of `{timestamp, faceCount}`; output: events and metrics. Rules: 0 faces for 3 s or more -> "no face" notice and one `no_face_event`; 2+ faces for 2 s or more -> multiple-faces notice and one `multi_face_event`; track visible percentage and longest absence.
- `useFaceDetector` runs MediaPipe FaceDetector at about 5 fps on the preview video (throttled, not per animation frame). Serve wasm and model from `public/mediapipe/` (download during setup; if impossible, use the official CDN and note it in `docs/decisions.md`). If the camera is denied or loading fails, continue without it.
- Wording is supportive: "We can't see you right now. Try adjusting your camera." and "More than one person is visible. For the best practice, sit alone if you can." Notices never block the interview. Never infer emotion, confidence or personality from the face. Never call anything "cheating" or "proctoring".

## 13. Diagnostics page (this is how we choose the best settings)

A plain-text page that runs and prints, with a "Copy results" button:
- Environment: browser, WebGPU adapter available (yes/no, adapter info), number of CPU cores, device memory if available.
- Mic and VAD test: speak a sentence, show segment duration and detection.
- STT test: record about 5 seconds, send to each provider in `STT_CHAIN` separately (a test parameter), print the text and milliseconds. Include a reference sentence to read so accuracy can be compared by eye, including the candidate's own accent.
- TTS test: speak a fixed sentence with each TTS engine and print time to first audio.
- LLM test: call `GET /api/diagnostics/providers`, print each provider's status and latency.
- Camera test: measured detection fps and face count.
- Database ping.

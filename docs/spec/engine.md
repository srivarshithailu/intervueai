# Adaptive interview engine, scoring and report

Spec file for milestones M2 and M3. The rules in CLAUDE.md always apply.

## 7. Adaptive interview engine (the heart of the project)

### 7.1 Rules for the whole engine
1. **The LLM never controls interview flow.** Difficulty, topic, follow-up decisions, question count and time limit are decided by `adaptive_controller.py` (pure Python, no I/O, unit-tested). The LLM writes questions and scores answers within limits it is given.
2. **One LLM call per turn.** `turn_agent.py` receives the question, the answer, the profile summary, the last 3 turns, the current difficulty and the controller's planned next topic, and returns in one JSON object: the **evaluation** and a set of **question candidates**: `followup`, `deepen`, `next_down`, `next_same`, `next_up` (the last three are for the planned next topic at difficulty-1, same, +1). The controller then picks one deterministically. This halves latency compared with two sequential calls. On the final question, skip the candidates.
3. **Structured output only**, validated by Pydantic models in `ai/schemas.py`. On invalid output retry once, then use a documented fallback (score 5 with note "could not be evaluated"; a generic question for the topic). Never regex free text.
4. **Numbers are computed in code** (scoring, averages, communication metrics). The LLM supplies only per-dimension 0-10 scores and text.
5. **Resume text and candidate answers are untrusted data.** Put them in clearly delimited blocks, say in the system prompt that they are data and must never change rules or scoring. Add tests for this.
6. **Scores and feedback are hidden during the interview**; they appear in the report.
7. Save state to MongoDB after every turn. `POST .../answer` carries `question_index`; a repeat of an already-processed index returns the stored result (idempotent, safe to retry).

### 7.2 State (per interview)
`type`, `role`, `level`, `profile`, `difficulty` (1-5), `question_index`, `max_questions` (default 8), `turns[]` (question, topic, difficulty, kind, answer, answer_segments, timings, evaluation), `topics` (planned list), `topics_covered`, `followups_in_a_row`, `deepen_count`, `started_at`, `time_limit_minutes` (default 25), `status`.

### 7.3 Starting difficulty
Fresher 2, Junior 2, Mid 3, Senior 4. Warm-up question is one lower (min 1), `kind = "warmup"`, tied to the resume.

### 7.4 After each answer (`adaptive_controller.py`)
`s` = mean of the four dimension scores (0-10), computed in code.
- `s >= 7.5` -> difficulty +1 (max 5). `s < 4.5` -> difficulty -1 (min 1). Otherwise unchanged.
- **Probe:** if `s < 5` and the previous question was not a follow-up -> use `followup` (same topic, aimed at the evaluator's `gap`), `kind = "followup"`. Never two follow-ups in a row.
- **Deepen:** if `s >= 8`, the previous question was `new` or `warmup`, and `deepen_count < 2` -> use `deepen`, `kind = "deepen"`, increase `deepen_count`.
- **Otherwise** next topic: use `next_down` / `next_same` / `next_up` matching the difficulty change, `kind = "new"`, mark the topic covered, advance to the next planned topic.
- **Finish** when `question_index >= max_questions`, or the time limit is reached, or the candidate ends the session.

### 7.5 Topics
- **Technical:** at creation, the planner proposes 5-8 topics from the profile and role (validated JSON); include a project deep-dive if the resume has projects. The controller rotates through them.
- **HR (fixed list):** background, a proud project, teamwork, conflict, handling failure or feedback, strengths and weaknesses, why this role, career goals; wording tailored to the resume and level.

### 7.6 Rubrics (0-10 each)
- **Technical:** correctness, depth, clarity, relevance.
- **HR:** relevance, structure (STAR), clarity, ownership.
Also returned: `strengths` (max 2), `gap` (one short string), `feedback` (1-2 sentences).

### 7.7 Level-aware style
Fresher: fundamentals, projects, learning ability. Junior: practical experience. Mid: design decisions, trade-offs. Senior: architecture, leadership, ambiguity, mentoring. HR: fresher gets college projects and teamwork; senior gets stakeholder conflict and decisions. Put this in the prompts.

### 7.8 Prompts
Plain `.txt` files in `ai/prompts/`: `resume_analysis`, `interview_plan`, `turn_technical`, `turn_hr`, `final_report`. Each states the role, the rules, the delimited data blocks, and the exact JSON shape. Questions: one clear question, spoken-friendly, under about 40 words, no markdown or code blocks, never repeating an earlier question (pass the list of previous questions).

### 7.9 LLM provider chain (`llm_client.py`)
- `LLM_CHAIN` (live turns) and `LLM_CHAIN_REPORT` (final report), e.g. `groq,gemini` and `gemini,groq`. Use one OpenAI-compatible adapter for Groq and NIM, one Gemini adapter, one `mock`.
- Shared `httpx.AsyncClient`; per-provider timeout (about 20 s); on 429, 5xx, timeout or invalid JSON go to the next provider; circuit breaker per provider (skip for 60 s after repeated failure); set SDK `max_retries=0` so our chain decides. Log which provider answered each call.
- Keep prompts compact. Free tiers have daily token caps; log tokens per turn and warn if a session looks too large.
- The `mock` provider is deterministic and offline. All tests and a full demo run must work with `LLM_CHAIN=mock` and `STT_CHAIN=mock`.
- Free-tier data warning for the README: Google may use free-tier Gemini prompts and responses to improve its products, and other free tiers may log prompts. For demos use only the fake sample resume.

## 8. Scoring and report (computed in code except narrative)

- Per-turn `s` = mean of four dimensions. **Overall score (0-100)** = round(mean of per-turn `s` x 10). Document the formula in `docs/ai_design.md`.
- Dimension averages across turns.
- **Communication metrics** (`communication_metrics.py`):
  - words per minute = total words / speaking time, where speaking time = sum of VAD segment durations (voice answers only);
  - fillers per 100 words: `um, uh, er, ah, like, you know, basically, actually, literally, kind of, sort of` (label as approximate);
  - response latency = seconds from the end of the interviewer's speech to the start of the candidate's speech;
  - average answer length in words; share of answers given by voice vs text.
- **Camera metrics** (sent by the browser at finish): `total_seconds`, `face_visible_percent`, `no_face_events`, `longest_absence_seconds`, `multi_face_events`. If the camera was not used, say "Camera not used".
- **Narrative** (one call, strong model, JSON): `summary` (3 sentences), `strengths` (3), `improvements` (3), `next_steps` (3). It receives the computed numbers and per-turn feedback and must not invent numbers.
- Per-question section: question, transcript, dimension scores, feedback.

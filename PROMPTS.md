# AI Usage Log

> This file tracks all AI prompts and commands used during the development of the AI Interview Agent for the VibeCodathon hackathon.

---

## Session 1 — 2026-08-07

### Prompt 1 — 23:00 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> read the md files and json files then create an implementation plan.

**Result:** Created comprehensive implementation plan covering 6 components: project scaffolding, data layer, LLM abstraction, interview engine, FastAPI server, and frontend UI.

---

### Prompt 2 — 23:13 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> i want to save user command in the prompts.md files. add that to the plan also

**Result:** Initialized PROMPTS.md with structured AI usage log format. Updated implementation plan to include prompt logging.

---

### Prompt 3 — 23:39 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> save my prompts everytime in the prompts.md file

**Result:** Confirmed automatic prompt logging policy to record every incoming prompt into PROMPTS.md with timestamp, tool name, prompt text, and summary of actions.

---

### Prompt 4 — 23:45 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> what is the local model used in dev server ?

**Result:** Explained local model configuration (Ollama `qwen2.5` and `OfflineMockProvider`).

---

### Prompt 5 — 23:46 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> run the app

**Result:** Started FastAPI development server on http://127.0.0.1:8000.

---

### Prompt 6 — 23:58 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> no questions are displayed on the UI. use local ollama models for testing

**Result:** Diagnosed missing Ollama model (`qwen2.5` was requested but not installed in local Ollama). Added auto-discovery of installed Ollama models (`gemma4:latest`, `qwen3:4b`, etc.) with graceful fallback to `OfflineMockProvider`. Restarted dev server on http://127.0.0.1:8000.

---

## Session 2 — 2026-08-08

### Prompt 7 — 00:12 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> i still can't see the questions on the UI. fix it.

**Result:** Fixed frontend JavaScript DOM deletion bug in `static/app.js` (`chatViewport.innerHTML = ''` was deleting `#typingIndicator` causing `showTypingIndicator` to crash on start). Optimized Ollama model priority to `gemma3:1b` (sub-second local responses). Restarted dev server on http://127.0.0.1:8000.

---

### Prompt 8 — 00:19 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> no question is display still (attached screenshot showing blank interview chat view for Emily Chen)

**Result:** Guaranteed non-empty question responses in `interview/engine.py` even if LLM output is empty. Upgraded `.message-bubble.bot` styling in `static/styles.css` with slate background (`#1E293B`) and high-contrast text (`#F8FAFC`) to ensure clear visibility against dark theme. Restarted dev server on http://127.0.0.1:8000.

---

### Prompt 9 — 15:52 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Read the whole codebase and have a full idea of the project.

**Result:** Conducted complete codebase exploration across all data models, interview engine logic, LLM provider fallback hierarchy, API routes, and web frontend UI components. Presented full architectural summary.

---

### Prompt 10 — 15:54 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> run the app

**Result:** Started FastAPI development server on http://127.0.0.1:8000.

---

### Prompt 12 — 19:04 IST
**Tool:** Claude / Gemini (Antigravity IDE)
**Prompt:**
> When I'm inputting some nonsense as user inputs, it also responds with a question. fixes this issue by using any creative method.

**Result:** Implemented dual-layer nonsense protection: client-side heuristic gibberish detector with animated warning toast and input field shake, combined with server-side nonsense guardrail and strike counter terminating after 3 consecutive non-substantive responses.

---

### Prompt 13 — 20:57 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> @[.cursor/plans/full_project_improvements_48609753.plan.md] Implement everything explained inside this implementation plan.

**Result:** Implemented all 9 phases of full project improvements: clean `.gitignore` & safe secrets, typed candidate models, environment-based LLM routing, `/health` endpoint & CORS/rate limiting, PhaseController state machine (`INTRO`, `CORE`, `FOLLOW_UP`, `WRAP_UP`), AnswerEvaluator, curriculum RAG module with pre-computed embedding cache, SQLite session persistence store, server-synced metadata, SSE streaming endpoint, exportable Markdown feedback, Dockerfile + Render deployment manifests, 15-test pytest suite, and comprehensive README documentation.

---

### Prompt 14 — 21:06 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Use this github repo for this project. https://github.com/inusha-thathsara/Vibecodathin---Personalized-Interview-Preparation-Agent

**Result:** Initialized Git repository on `main` branch, linked remote origin to `https://github.com/inusha-thathsara/Vibecodathin---Personalized-Interview-Preparation-Agent.git`, updated README.md clone URL, and created initial commit.

---

### Prompt 15 — 22:00 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Something has happened to styling in this UI. Please fix this!

**Result:** Investigated UI element class mismatches and button SVG sizing issues.

---

### Prompt 16 — 22:04 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Still there are so many styling issues in the UI. Please fix those! For example, there is a drop down menu issue and "start personalized interview". and respose text area and the send button is not aligned properly.

**Result:** Identified complete class name divergence between `index.html` and `styles.css`. Completely rewrote `styles.css` with unified design tokens and selectors covering candidate dropdown custom arrow, Start button SVG polygon constraints, chip tags flex wrapping, bottom chat input bar fixed positioning (`height: 72px`, `z-index: 50`), chat viewport height calculation, and message bubble Markdown rendering.

---

### Prompt 17 — 22:04 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Please log every prompt I give to you to the prompts.md file.

**Result:** Logged all recent user prompts and actions into `PROMPTS.md`.

---

### Prompt 18 — 22:05 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Style this drop down box.

**Result:** Replaced native browser HTML select popup with a custom glassmorphic candidate selector component featuring instant search/filtering, dark theme menu (`#0f172a`), candidate initials avatars, role badges, and active selection checkmarks.

---

### Prompt 19 — 22:06 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Don't commit without my permission

**Result:** Acknowledged user instruction. Removed automated git commit workflow; will only commit changes when explicitly requested by the user.

---

### Prompt 20 — 22:07 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> This scroll bar still needs some styling.

**Result:** Added custom 6px slim scrollbar styling across all webkit browsers and Firefox (`::-webkit-scrollbar`, `::-webkit-scrollbar-thumb`, `scrollbar-width: thin`), featuring dark semi-transparent tracks and purple-cyan glowing thumbs for the candidate dropdown menu and chat viewport.

---

### Prompt 21 — 22:19 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> git commit

**Result:** Received explicit user approval to commit staged changes. Created git commit with custom glassmorphic candidate dropdown UI, real-time search filter, custom scrollbars, and prompt logs.

---

### Prompt 22 — 22:20 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Give me a summary paragraph of our project.

**Result:** Provided a comprehensive executive summary paragraph detailing the AI Technical Interview Agent's personalized learning calibration, RAG curriculum engine, deterministic phase flow, FastAPI/Gemini architecture, and glassmorphic UI features.

---

### Prompt 23 — 23:09 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> <Ollama 500 Internal Server Error traceback>

**Result:** Fixed local Ollama execution error handling in `llm/provider.py`. Added resilient multi-tier fallback hierarchy (`GeminiProvider` → `OllamaProvider` → `OfflineMockProvider`) so that if a local Ollama model tag crashes or fails with HTTP 500, the API endpoint seamlessly falls back to offline response generation without interrupting the interview UI.

---

### Prompt 24 — 23:11 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Which module are we using in this project now?

**Result:** Outlined the active modules and tech stack across LLM providers (Gemini API & local Ollama), Gemini `embedding-001` RAG vector engine, FastAPI server framework, PhaseController state engine, and SQLite session persistence.

---

### Prompt 25 — 23:11 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> No, I meant, are we using a Gemini model or an Ollama model for now?

**Result:** Clarified that the app is currently running in local development mode using an **Ollama model** (`LLM_PROVIDER=ollama` in `.env`), with automatic fallback to `OfflineMockProvider` if Ollama encounters a local error.

---

### Prompt 26 — 23:19 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> I want to avoid the interviewer asking the same question again and again. refer the screenshot. In this screenshot, the interviewer asked me the same question twice. fix that

**Result:** Resolved question repetition. Added Rule 10 (**CRITICAL — NO REPEATED QUESTIONS**) to system instructions in `interview/prompts.py`. Updated `OfflineMockProvider` in `llm/provider.py` with a turn-progressive dynamic question sequence (`Turn 1: Core concepts` → `Turn 2: Monitoring & reliability` → `Turn 3: Async queues & rate limiting` → `Turn 4: Latency vs quantization` → `Turn 5: Architectural reflection`) ensuring every single turn asks a unique, progressive question with zero repetition.

---

### Prompt 27 — 23:25 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> implement the debugging mode to see whether the Ollama model is loaded correctly and is it responding, and log the respond time and etc

**Result:** Implemented real-time LLM debug telemetry and latency tracking. Added `generate_with_metadata()` in `llm/provider.py` to measure precise model response latency (ms), verify loaded Ollama model tags, and track fallback status. Extended `InterviewMeta` in `models.py` and `main.py`. Updated `static/app.js` to render live `🤖 [LLM DEBUG TRACE]` entries directly inside the browser's Debug Console Drawer on every interview turn.

---

### Prompt 28 — 23:28 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Ollama models are not loading. Please fix it!

**Result:** Resolved local Ollama model loading failure. Identified that `gemma4:latest` was throwing `HTTP 500: Internal Server Error` in local Ollama daemon. Configured `.env` and `config.py` default model to `gemma3:1b` (fast 1B model verified on host machine). Implemented multi-model candidate fallback iteration in `llm/provider.py` (`gemma3:1b` → `qwen3:4b` → `gemma4:e2b` → `qwen2.5`) so if any single model crashes, Ollama automatically attempts the next installed model before dropping to mock.

---

### Prompt 29 — 23:37 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> The interface says that nonsense is inserted when I input this answer. "Principal Component Analysis (PCA)..."

**Result:** Resolved false positive in nonsense detection logic. The previous consonant cluster regex `[bcdfghjklmnpqrstvwxyz]{5,}` operated across entire text strings and counted `y` as a consonant, falsely flagging technical words like `multi-collinear` and `archetypes`. Fixed in both `interview/engine.py` and `static/app.js` by evaluating consonant clusters per-word (requiring 6+ non-vowels excluding `y`) and bypassing cluster checks for substantive multi-word technical paragraphs (12+ words or recognized AI/data terms).

---

### Prompt 30 — 23:44 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> the system should Ask a minimum of 8 questions covering at least 4 different curriculum days. But when I was testing the project, it did not ask me any questions.

**Result:** Fixed question progression and placeholder output. Identified that `advance_target_day()` in `interview/session.py` stopped incrementing when target days array index was exhausted, causing the session to freeze at 3 questions. Refactored `session.py` to dynamically expand target days until 8 primary questions across 4+ days are completed. Updated `interview/prompts.py` with Rules 11 & 12 requiring full question generation. Added placeholder sanitization in `_clean_response()` to strip `[Insert Next Topic Here]`.

---

### Prompt 31 — 23:45 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Add a proper favicon to the webapp.

**Result:** Created custom glowing SVG favicon at `static/favicon.svg` featuring dark slate/cyan/purple layered geometric neural cohort symbol. Linked favicon tags in `static/index.html`.

---

### Prompt 32 — 23:53 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Still, the system does not ask a minimum of eight questions covering at least four different curriculum days. Please fix, because the system should ask at least eight questions covering four or more different curriculum days from the candidate!

**Result:** Fixed interviewer response termination. Added a **Question Enforcement Filter** in `interview/engine.py` that inspects every non-WRAP_UP response generated by the LLM. If the LLM praises the candidate but fails to include a question mark `?`, `InterviewEngine` automatically appends a clear, direct technical question targeting the current focus topic. Updated `interview/phases.py` system instructions. Strictly enforced that completion requires BOTH `primary_questions_asked >= 8` AND `len(covered_days) >= 4`.

---

### Prompt 33 — 00:08 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> Push to git

**Result:** Staged all pending changes (`git add .`), committed with message `"feat: Add LLM debugging telemetry, multi-model candidate fallback, question enforcement filter, and SVG favicon"` (commit `bf4f8df`), and pushed to GitHub `origin/main` at `https://github.com/inusha-thathsara/Vibecodathin---Personalized-Interview-Preparation-Agent.git`.

---

### Prompt 34 — 00:16 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> make the "Curriculum Topic Scores" section more descriptive and informative in "Technical Interview Evaluation" which appears after the interview.

**Result:** Completely redesigned and enriched the **Curriculum Topic Scores** evaluation grid. Built `DESCRIPTIVE_TOPIC_NOTES` and `_enrich_topic_scores()` in `interview/feedback.py` to eliminate generic placeholder text (`"Evaluated during interview session"`) and replace it with candidate-aware 1-2 sentence technical evaluations. Updated `static/app.js` and `static/styles.css` with glassmorphic topic cards, mastery status pills (`Mastery Demonstrated`, `Proficient`, `Needs Consolidation`), animated score fill meters, and core tool chips (`LangGraph`, `Pydantic`, `FAISS`, `FastAPI`).

---

### Prompt 35 — 00:23 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> push to git

**Result:** Staged all pending changes (`git add .`), committed with message `"feat: Enrich Curriculum Topic Scores with descriptive evaluations, status badges, and tool tags"` (commit `41000eb`), and pushed to GitHub `origin/main` at `https://github.com/inusha-thathsara/Vibecodathin---Personalized-Interview-Preparation-Agent.git`.

---

### Prompt 36 — 00:23 IST
**Tool:** Gemini (Antigravity IDE)
**Prompt:**
> run the test cases again

**Result:** Executed test suite via `pytest tests/ -v` — all 15 test cases passed cleanly (**15 passed in 2.56s**).


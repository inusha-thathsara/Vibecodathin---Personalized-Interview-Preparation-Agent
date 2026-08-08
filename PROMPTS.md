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


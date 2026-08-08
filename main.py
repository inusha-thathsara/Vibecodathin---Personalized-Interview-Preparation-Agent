import logging
import json
import time
from typing import Dict
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

import config
from models import InterviewRequest, InterviewResponse, FeedbackSchema, InterviewMeta
from interview.session import session_manager, InterviewSession
from interview.engine import InterviewEngine
from llm.health import check_llm_health
from rag.indexer import curriculum_indexer
from data.loader import data_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_interview_agent")

app = FastAPI(
    title="AI Interview Agent API",
    description="Personalized Technical Interview Agent for AI Engineering Cohort",
    version="1.0.0"
)

# CORS setup
origins = [o.strip() for o in config.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiting middleware
RATE_LIMIT_STORE: Dict[str, list] = {}
RATE_LIMIT_MAX = 40  # requests
RATE_LIMIT_WINDOW = 60  # seconds

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/interview"):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        timestamps = [t for t in RATE_LIMIT_STORE.get(client_ip, []) if now - t < RATE_LIMIT_WINDOW]
        if len(timestamps) >= RATE_LIMIT_MAX:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please wait a moment before sending more messages."}
            )
        timestamps.append(now)
        RATE_LIMIT_STORE[client_ip] = timestamps

    response = await call_next(request)
    return response

@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting AI Interview Agent in APP_ENV='{config.APP_ENV}', LLM_PROVIDER='{config.LLM_PROVIDER}'")
    try:
        check_llm_health()
    except Exception as e:
        logger.error(f"Startup health probe issue: {e}")

    try:
        curriculum_indexer.initialize_index()
    except Exception as e:
        logger.warning(f"RAG Indexer initialization warning: {e}")

def _build_meta(session: InterviewSession) -> InterviewMeta:
    target_day = session.get_current_target_day()
    day_info = data_loader.get_day_info(target_day) or {}
    llm_meta = getattr(session, "last_llm_meta", {}) or {}

    return InterviewMeta(
        phase=session.phase,
        primary_questions=session.primary_questions_asked,
        days_covered=sorted(list(session.covered_days)),
        current_day=target_day,
        current_title=day_info.get("title", f"Day {target_day}"),
        llm_provider=llm_meta.get("provider", config.LLM_PROVIDER),
        llm_model=llm_meta.get("model", config.OLLAMA_MODEL),
        llm_latency_ms=llm_meta.get("latency_ms", 0.0),
        llm_status=llm_meta.get("status", "success"),
        llm_fallback=llm_meta.get("fallback", False)
    )

@app.get("/health")
async def health_check():
    """Health status endpoint per spec."""
    return check_llm_health()

@app.post("/api/interview", response_model=InterviewResponse)
async def handle_interview(req: InterviewRequest):
    """
    Main interview endpoint per Technical Specification.
    - Start interview: req contains sessionId and candidate object
    - Conversation turn: req contains sessionId and message
    - End interview: returns done=True and structured feedback
    """
    session_id = req.sessionId
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId is required")

    try:
        # 1. Start Interview case
        if req.candidate is not None:
            cand_dict = req.candidate.dict()
            session = session_manager.get_or_create_session(session_id, cand_dict)
            opening_reply = InterviewEngine.start_interview(session)
            session_manager.save_session(session)
            return InterviewResponse(
                reply=opening_reply,
                done=False,
                meta=_build_meta(session)
            )

        # 2. Conversation Turn case
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found. Please initialize session with candidate data first."
            )

        if session.is_complete:
            feedback_data = session.feedback or {}
            feedback = FeedbackSchema(**feedback_data) if feedback_data else None
            return InterviewResponse(
                reply="The interview is already completed. Thank you!",
                done=True,
                feedback=feedback,
                meta=_build_meta(session)
            )

        # 3. End Early case
        if req.endEarly:
            reply, done, feedback_data = InterviewEngine.end_interview_early(session)
            session_manager.save_session(session)
            feedback = FeedbackSchema(**feedback_data) if feedback_data else None
            return InterviewResponse(
                reply=reply,
                done=True,
                feedback=feedback,
                meta=_build_meta(session)
            )

        user_message = req.message or ""
        reply, done, feedback_data = InterviewEngine.process_turn(session, user_message)
        session_manager.save_session(session)

        feedback = FeedbackSchema(**feedback_data) if feedback_data else None
        return InterviewResponse(
            reply=reply,
            done=done,
            feedback=feedback,
            meta=_build_meta(session)
        )

    except Exception as e:
        logger.exception(f"Error handling interview turn for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Interview engine error: {str(e)}"
        )

@app.post("/api/interview/stream")
async def stream_interview(req: InterviewRequest):
    """
    Optional Server-Sent Events (SSE) streaming endpoint for real-time response delivery.
    """
    session_id = req.sessionId
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId is required")

    session = session_manager.get_session(session_id)
    if not session and req.candidate:
        session = session_manager.get_or_create_session(session_id, req.candidate.dict())

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    def sse_generator():
        if req.candidate and len(session.messages) == 0:
            reply = InterviewEngine.start_interview(session)
            done = False
            feedback_data = None
        else:
            reply, done, feedback_data = InterviewEngine.process_turn(session, req.message or "")

        session_manager.save_session(session)

        # Stream text chunks
        chunk_size = 12
        for i in range(0, len(reply), chunk_size):
            chunk = reply[i:i + chunk_size]
            yield f"data: {json.dumps({'token': chunk})}\n\n"
            time.sleep(0.02)

        meta_data = _build_meta(session).dict()
        yield f"data: {json.dumps({'done': done, 'feedback': feedback_data, 'meta': meta_data})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.get("/api/candidates")
async def list_candidates():
    """Returns candidate profiles from candidates.json for frontend UI selection."""
    return {"candidates": data_loader.get_all_candidates()}

# Serve static frontend files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse({"message": "AI Interview Agent API is running."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

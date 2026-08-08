import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

# Force offline mock LLM mode for deterministic test environment
os.environ["APP_ENV"] = "test"
os.environ["LLM_PROVIDER"] = "mock"

import config
config.APP_ENV = "test"
config.LLM_PROVIDER = "mock"

from main import app
from data.loader import data_loader

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"

def test_candidates_endpoint():
    res = client.get("/api/candidates")
    assert res.status_code == 200
    data = res.json()
    assert "candidates" in data
    assert len(data["candidates"]) > 0

def test_full_interview_flow():
    candidates = data_loader.get_all_candidates()
    cand = candidates[0]
    session_id = "test_sess_api_123"

    # Start interview
    res = client.post("/api/interview", json={
        "sessionId": session_id,
        "candidate": cand
    })
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert data["done"] is False
    assert "meta" in data
    assert data["meta"]["phase"] in ("INTRO", "CORE")

    # Turn 1
    res_turn = client.post("/api/interview", json={
        "sessionId": session_id,
        "message": "I used vector embeddings and cosine similarity to index domain documents."
    })
    assert res_turn.status_code == 200
    turn_data = res_turn.json()
    assert "reply" in turn_data
    assert "meta" in turn_data

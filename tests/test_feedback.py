import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interview.session import InterviewSession
from interview.feedback import generate_feedback
from data.loader import data_loader

def test_generate_feedback_schema():
    candidates = data_loader.get_all_candidates()
    cand = candidates[0]
    session = InterviewSession("test_feedback_sess", cand)

    session.add_user_message("I implemented RAG using vector search.")
    session.add_assistant_message("Good, how did you handle metadata filters?")
    session.add_user_message("I applied metadata filtering prior to vector similarity calculations.")
    session.mark_day_covered(7)
    session.mark_day_covered(8)

    fb = generate_feedback(session)
    assert "summary" in fb
    assert "strengths" in fb
    assert "gaps" in fb
    assert "next" in fb
    assert isinstance(fb["strengths"], list)
    assert isinstance(fb["gaps"], list)
    assert isinstance(fb["next"], list)
    assert "topic_scores" in fb
    assert "evidence" in fb

def test_generate_feedback_zero_responses():
    candidates = data_loader.get_all_candidates()
    cand = candidates[0]
    session = InterviewSession("test_zero_resp_sess", cand)

    # Session initialized but ended immediately without candidate answers
    fb = generate_feedback(session)
    assert "summary" in fb
    assert "ended early before any candidate responses" in fb["summary"]
    assert "strengths" in fb
    assert "gaps" in fb
    assert fb["topic_scores"][0]["score"] == 0
    assert "terminated early" in fb["topic_scores"][0]["note"].lower()

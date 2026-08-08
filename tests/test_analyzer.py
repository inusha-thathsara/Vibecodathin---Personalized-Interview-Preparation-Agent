import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.loader import data_loader
from data.analyzer import CandidateAnalyzer

def test_candidate_loader():
    candidates = data_loader.get_all_candidates()
    assert len(candidates) > 0, "Candidates list should not be empty."

def test_candidate_analyzer_basic():
    candidates = data_loader.get_all_candidates()
    sample = candidates[0]
    analysis = CandidateAnalyzer.analyze(sample)

    assert "name" in analysis
    assert "jobRole" in analysis
    assert "difficulty" in analysis
    assert "engagement_score" in analysis
    assert 0.0 <= analysis["engagement_score"] <= 1.0
    assert len(analysis["target_days"]) > 0
    assert "mission_summary" in analysis

def test_candidate_analyzer_difficulty_calibration():
    senior_cand = {
        "member": {"name": "Senior Dev", "jobRole": "Lead Engineer", "yearsExperience": 12},
        "missions": [],
        "signals": {}
    }
    analysis = CandidateAnalyzer.analyze(senior_cand)
    assert analysis["difficulty"] == "senior"

    junior_cand = {
        "member": {"name": "Junior Dev", "jobRole": "Intern", "yearsExperience": 1},
        "missions": [],
        "signals": {}
    }
    analysis_jr = CandidateAnalyzer.analyze(junior_cand)
    assert analysis_jr["difficulty"] == "foundational"

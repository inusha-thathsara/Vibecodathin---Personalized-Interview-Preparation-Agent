import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interview.phases import PhaseController

def test_phase_intro_to_core():
    next_p = PhaseController.determine_next_phase(
        current_phase="INTRO",
        primary_questions_asked=1,
        covered_days_count=1,
        last_answer_quality="accurate",
        follow_ups_on_current_day=0
    )
    assert next_p == "CORE"

def test_phase_core_to_follow_up():
    next_p = PhaseController.determine_next_phase(
        current_phase="CORE",
        primary_questions_asked=2,
        covered_days_count=1,
        last_answer_quality="partial",
        follow_ups_on_current_day=0
    )
    assert next_p == "FOLLOW_UP"

def test_phase_force_wrap_up():
    next_p = PhaseController.determine_next_phase(
        current_phase="CORE",
        primary_questions_asked=8,
        covered_days_count=4,
        last_answer_quality="accurate",
        follow_ups_on_current_day=0
    )
    assert next_p == "WRAP_UP"

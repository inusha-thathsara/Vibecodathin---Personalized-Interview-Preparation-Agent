import logging
from typing import Literal

logger = logging.getLogger(__name__)

PhaseType = Literal["INTRO", "CORE", "FOLLOW_UP", "WRAP_UP"]

class PhaseController:
    @staticmethod
    def determine_next_phase(
        current_phase: PhaseType,
        primary_questions_asked: int,
        covered_days_count: int,
        last_answer_quality: str,
        follow_ups_on_current_day: int,
        max_follow_ups: int = 2
    ) -> PhaseType:
        """
        Determines the next interview phase deterministically based on progress and quality.
        """
        # Rule 1: Force WRAP_UP when minimum requirements met (>= 8 primary questions and >= 4 days covered)
        if primary_questions_asked >= 8 and covered_days_count >= 4:
            return "WRAP_UP"

        # Rule 2: INTRO transitions to CORE after initial greeting/question
        if current_phase == "INTRO":
            return "CORE"

        # Rule 3: Handling WRAP_UP
        if current_phase == "WRAP_UP":
            return "WRAP_UP"

        # Rule 4: Handling FOLLOW_UP state
        if current_phase == "FOLLOW_UP":
            if follow_ups_on_current_day >= max_follow_ups or last_answer_quality in ("accurate", "strong"):
                return "CORE"
            return "FOLLOW_UP"

        # Rule 5: Handling CORE state
        if current_phase == "CORE":
            if last_answer_quality in ("partial", "weak", "incorrect") and follow_ups_on_current_day < max_follow_ups:
                return "FOLLOW_UP"
            return "CORE"

        return "CORE"

    @staticmethod
    def get_phase_instructions(phase: PhaseType, session) -> str:
        """
        Returns exact phase-specific behavioral instructions to append to the system prompt.
        """
        if phase == "INTRO":
            return (
                "### CURRENT PHASE: INTRO\n"
                "Welcome the candidate warmly and ask the FIRST technical question targeting their initial curriculum focus. "
                "Keep the greeting brief (1-2 sentences) and jump straight into the technical topic."
            )

        elif phase == "FOLLOW_UP":
            return (
                "### CURRENT PHASE: FOLLOW_UP\n"
                "The candidate's previous response was partial, weak, or incomplete. "
                "Ask a targeted, probing follow-up question to help them clarify their understanding or uncover knowledge gaps. "
                "Do NOT move to a new topic yet."
            )

        elif phase == "CORE":
            return (
                "### CURRENT PHASE: CORE INTERVIEW\n"
                "Acknowledge the candidate's previous response succinctly (1 sentence). "
                "Then, transition smoothly to the planned curriculum focus and ask ONE clear, focused technical question. YOUR RESPONSE MUST END WITH A DIRECT TECHNICAL QUESTION ENDING WITH A QUESTION MARK ('?')."
            )

        elif phase == "WRAP_UP":
            return (
                "### CURRENT PHASE: WRAP_UP\n"
                "The candidate has satisfied the core interview evaluation requirements (minimum 8 primary questions across 4+ curriculum modules). "
                "Politely conclude the interview with a concise closing remark summarizing their performance, "
                "and append the exact token `[INTERVIEW_COMPLETE]` at the very end of your response."
            )

        return ""

import re
import logging
from typing import Dict, Any, Tuple, Optional
from interview.session import InterviewSession
from interview.prompts import INTERVIEWER_SYSTEM_PROMPT
from interview.feedback import generate_feedback
from interview.phases import PhaseController
from interview.evaluator import AnswerEvaluator
from rag.retriever import CurriculumRetriever
from llm.provider import get_llm_provider
from data.loader import data_loader

logger = logging.getLogger(__name__)

_LOW_EFFORT_WORDS = {
    'hi','hello','hey','yo','sup','lol','lmao','bruh','haha','ok','hmm',
    'idk','nah','meh','wat','huh','wow','omg','nice','cool','test','asdf',
    'qwerty','asd','xyz','yes','no','bye','thanks','thank'
}

class InterviewEngine:
    @staticmethod
    def _is_nonsense(text: str) -> bool:
        """Server-side heuristic nonsense detector."""
        cleaned = text.strip()
        if len(cleaned) < 4:
            return True

        words = [w for w in re.split(r'\s+', cleaned) if w]
        alpha_only = re.sub(r'[^a-zA-Z]', '', cleaned).lower()
        if alpha_only in _LOW_EFFORT_WORDS:
            return True

        if re.search(r'(.)\1{6,}', cleaned):
            return True

        # If response is a multi-word technical paragraph (5+ words), check recognized vocabulary
        if len(words) >= 5:
            _common = {
                'the','be','to','of','and','a','in','that','have','i','it','for','not',
                'on','with','is','are','was','this','but','by','from','they','we','you',
                'do','at','or','an','will','my','what','so','up','out','if','about','can',
                'how','all','no','just','know','get','use','make','like','would','could',
                'vector','embedding','database','model','training','data','api','server',
                'agent','prompt','rag','retrieval','query','token','llm','code','python',
                'docker','kubernetes','security','memory','context','pipeline','network',
                'deploy','function','architecture','production','monitoring','testing',
                'pca','principal','component','analysis','clustering','segmentation',
                'variance','overfitting','feature','preprocessing','correlated','metrics',
                'telemetry','latent','behavioral','archetypes','user','churn','models'
            }
            recognized = sum(1 for w in words if re.sub(r'[^a-z]', '', w.lower()) in _common)
            ratio = recognized / len(words)
            if ratio >= 0.15 or len(words) >= 15:
                return False

        # Individual word consonant cluster check (6+ consonants, excluding 'y')
        for w in words:
            clean_w = re.sub(r'[^a-zA-Z]', '', w)
            if re.search(r'[bcdfghjklmnpqrstvwxz]{6,}', clean_w, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def start_interview(session: InterviewSession) -> str:
        """Initializes the interview and returns the opening question."""
        analysis = session.analysis
        llm = get_llm_provider()

        session.phase = "INTRO"
        target_day = session.get_current_target_day()
        day_info = data_loader.get_day_info(target_day) or {}
        session.mark_day_covered(target_day)

        retrieved_context = CurriculumRetriever.retrieve_context(target_day, "start interview", top_k=2)
        phase_instructions = PhaseController.get_phase_instructions("INTRO", session)

        system_prompt = INTERVIEWER_SYSTEM_PROMPT.format(
            name=analysis.get("name", "Candidate"),
            job_role=analysis.get("jobRole", "Software Engineer"),
            years_exp=analysis.get("yearsExperience", 0),
            education=analysis.get("education", ""),
            difficulty=analysis.get("difficulty", "intermediate"),
            engagement_score=analysis.get("engagement_score", 0.8),
            mission_summary=analysis.get("mission_summary", ""),
            primary_questions=0,
            days_covered=list(session.covered_days),
            current_target_day=target_day,
            current_target_title=day_info.get("title", f"Day {target_day}"),
            current_target_tools=", ".join(day_info.get("tools", [])),
            current_target_objectives="; ".join(day_info.get("objectives", [])),
            retrieved_context=retrieved_context,
            phase_instructions=phase_instructions
        )

        messages = [
            {"role": "user", "content": "Please start the technical interview. Welcome me briefly and ask the first question."}
        ]

        response, llm_meta = llm.generate_with_metadata(messages, system_prompt=system_prompt)
        session.last_llm_meta = llm_meta
        cleaned_reply, is_done = InterviewEngine._clean_response(response)
        
        if not cleaned_reply:
            cleaned_reply = f"Welcome {analysis.get('name', 'Candidate')}! Let's begin your technical interview. Could you explain the core concepts of {day_info.get('title', 'Day ' + str(target_day))} and how you implemented them during the cohort?"

        session.phase = "CORE"
        session.add_assistant_message(cleaned_reply, is_primary_question=True)
        return cleaned_reply

    @staticmethod
    def process_turn(session: InterviewSession, user_message: str) -> Tuple[str, bool, Any]:
        """Processes candidate response, advances conversation, returns (reply, done, feedback)."""
        
        # 1. Server-side nonsense guard
        is_nonsense = InterviewEngine._is_nonsense(user_message)
        if is_nonsense:
            session.nonsense_strikes += 1
            logger.warning(
                f"Nonsense detected (strike {session.nonsense_strikes}) "
                f"for session {session.session_id}: '{user_message[:60]}'"
            )

            if session.nonsense_strikes >= 3:
                session.is_complete = True
                session.phase = "WRAP_UP"
                session.add_user_message(user_message)
                termination_reply = (
                    "I've noticed that you haven't provided substantive technical responses "
                    "to the interview questions. Unfortunately, I'm unable to continue the "
                    "evaluation without meaningful engagement. The interview will be concluded now."
                )
                session.add_assistant_message(termination_reply)
                feedback = {
                    "summary": f"{session.analysis.get('name', 'Candidate')} did not engage meaningfully with the technical interview questions. Multiple responses were non-substantive or contained gibberish, making a fair technical evaluation impossible.",
                    "strengths": ["Showed willingness to participate in the interview process"],
                    "gaps": [
                        "Failed to provide substantive technical responses",
                        "Did not demonstrate understanding of core AI cohort concepts",
                        "Interview engagement was insufficient for proper evaluation"
                    ],
                    "next": [
                        "Review all cohort materials thoroughly before re-attempting the interview",
                        "Practice articulating technical concepts clearly and concisely",
                        "Prepare specific examples from hands-on cohort projects"
                    ],
                    "topic_scores": [],
                    "evidence": [f"User input: {user_message[:50]}..."]
                }
                session.feedback = feedback
                return termination_reply, True, feedback

        session.add_user_message(user_message)
        analysis = session.analysis
        llm = get_llm_provider()

        target_day = session.get_current_target_day()
        day_info = data_loader.get_day_info(target_day) or {}
        target_title = day_info.get("title", f"Day {target_day}")

        # 2. Evaluate candidate answer
        eval_result = AnswerEvaluator.evaluate(target_day, target_title, user_message)
        last_quality = eval_result.get("quality", "partial")
        session.last_answer_quality = last_quality

        # 3. Determine next phase and target day progression
        next_phase = PhaseController.determine_next_phase(
            current_phase=session.phase,
            primary_questions_asked=session.primary_questions_asked,
            covered_days_count=len(session.covered_days),
            last_answer_quality=last_quality,
            follow_ups_on_current_day=session.follow_ups_on_current_day
        )
        session.phase = next_phase

        # Advance topic if moving to CORE from accurate/solid answer or max follow-ups
        is_primary = False
        if session.phase == "CORE" and not is_nonsense:
            if last_quality in ("accurate", "strong") or session.follow_ups_on_current_day >= 2:
                session.advance_target_day()
                target_day = session.get_current_target_day()
                day_info = data_loader.get_day_info(target_day) or {}
                target_title = day_info.get("title", f"Day {target_day}")
                session.mark_day_covered(target_day)
                is_primary = True

        # 4. RAG context & Phase instructions
        retrieved_context = CurriculumRetriever.retrieve_context(target_day, user_message, top_k=2)
        phase_instructions = PhaseController.get_phase_instructions(session.phase, session)

        system_prompt = INTERVIEWER_SYSTEM_PROMPT.format(
            name=analysis.get("name", "Candidate"),
            job_role=analysis.get("jobRole", "Software Engineer"),
            years_exp=analysis.get("yearsExperience", 0),
            education=analysis.get("education", ""),
            difficulty=analysis.get("difficulty", "intermediate"),
            engagement_score=analysis.get("engagement_score", 0.8),
            mission_summary=analysis.get("mission_summary", ""),
            primary_questions=session.primary_questions_asked,
            days_covered=list(session.covered_days),
            current_target_day=target_day,
            current_target_title=target_title,
            current_target_tools=", ".join(day_info.get("tools", [])),
            current_target_objectives="; ".join(day_info.get("objectives", [])),
            retrieved_context=retrieved_context,
            phase_instructions=phase_instructions
        )

        # Context compression: send system prompt + recent turns (last 6 messages)
        recent_messages = session.messages[-6:] if len(session.messages) > 6 else session.messages

        response, llm_meta = llm.generate_with_metadata(recent_messages, system_prompt=system_prompt)
        session.last_llm_meta = llm_meta
        cleaned_reply, is_done_signal = InterviewEngine._clean_response(response, target_title=target_title)

        if not cleaned_reply:
            if is_nonsense:
                cleaned_reply = "I notice that response didn't address the technical question. Could you please provide a substantive answer? Let me rephrase the question for you."
            elif session.phase == "FOLLOW_UP":
                cleaned_reply = f"Could you expand on your implementation details for {target_title}? Specifically, how did you handle edge cases and error handling?"
            else:
                cleaned_reply = f"Thank you for that response. Moving to {target_title}, how did you design and optimize your implementation during your cohort project?"

        # Question Enforcement Filter: Guarantee non-WRAP_UP responses always contain a direct question mark
        if "?" not in cleaned_reply and session.phase != "WRAP_UP":
            logger.info(f"LLM response lacked a question mark for '{target_title}'. Injecting topic-aligned question.")
            if session.phase == "FOLLOW_UP":
                cleaned_reply += f"\n\nFollowing up on {target_title}: Could you expand on how you handled edge cases and system performance bottlenecks in your project?"
            else:
                cleaned_reply += f"\n\nTransitioning to Day {target_day} — {target_title}: Could you explain your core architecture design and how you validated system performance during your cohort project?"
                is_primary = True

        # 5. Check completion criteria (minimum 8 primary questions AND minimum 4 days covered)
        force_completion = (session.phase == "WRAP_UP" or (session.primary_questions_asked >= 8 and len(session.covered_days) >= 4))

        if force_completion or is_done_signal:
            session.is_complete = True
            session.phase = "WRAP_UP"
            session.add_assistant_message(cleaned_reply, is_primary_question=False)
            feedback = generate_feedback(session)
            session.feedback = feedback
            return cleaned_reply, True, feedback

        session.add_assistant_message(cleaned_reply, is_primary_question=is_primary)
        return cleaned_reply, False, None

    @staticmethod
    def _clean_response(raw_text: str, target_title: str = "") -> Tuple[str, bool]:
        is_done = "[INTERVIEW_COMPLETE]" in raw_text
        cleaned = raw_text.replace("[INTERVIEW_COMPLETE]", "").strip()

        placeholders = [
            "[Insert Next Topic Here]", "[Next Topic Here]", "[Insert Topic]",
            "[Topic Name]", "[Insert Question]", "[Next Question]", "[Insert Next Question]",
            "[Insert Next Topic]", "[Topic]"
        ]
        for ph in placeholders:
            if ph in cleaned:
                topic_str = f"{target_title}" if target_title else "our next focus area"
                cleaned = cleaned.replace(ph, topic_str)

        return cleaned, is_done

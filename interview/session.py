import time
from typing import Dict, Any, List, Set, Optional
from data.analyzer import CandidateAnalyzer

class InterviewSession:
    def __init__(self, session_id: str, candidate_data: Dict[str, Any]):
        self.session_id = session_id
        self.raw_candidate = candidate_data
        self.analysis = CandidateAnalyzer.analyze(candidate_data)
        self.messages: List[Dict[str, str]] = []
        self.questions_asked: int = 0
        self.primary_questions_asked: int = 0
        self.follow_ups_on_current_day: int = 0
        self.covered_days: Set[int] = set()
        self.is_complete: bool = False
        self.feedback: Optional[Dict[str, Any]] = None
        self.current_target_index: int = 0
        self.nonsense_strikes: int = 0

        self.phase: str = "INTRO"
        self.last_answer_quality: Optional[str] = None
        self.interview_notes: str = ""
        self.created_at: float = time.time()
        self.last_active_at: float = time.time()

    def touch(self):
        self.last_active_at = time.time()

    def add_user_message(self, content: str):
        self.touch()
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str, is_primary_question: bool = False):
        self.touch()
        self.messages.append({"role": "assistant", "content": content})
        self.questions_asked += 1
        if is_primary_question:
            self.primary_questions_asked += 1
            self.follow_ups_on_current_day = 0
        else:
            self.follow_ups_on_current_day += 1

    def mark_day_covered(self, day_num: int):
        if day_num:
            self.covered_days.add(day_num)

    def get_current_target_day(self) -> int:
        target_days = self.analysis.get("target_days", [7])
        if not target_days:
            return 7
        idx = min(self.current_target_index, len(target_days) - 1)
        return target_days[idx]

    def advance_target_day(self):
        target_days = self.analysis.get("target_days", [])
        if self.current_target_index < len(target_days) - 1:
            self.current_target_index += 1
            self.follow_ups_on_current_day = 0

    def reset_day_follow_ups(self):
        self.follow_ups_on_current_day = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "raw_candidate": self.raw_candidate,
            "messages": self.messages,
            "questions_asked": self.questions_asked,
            "primary_questions_asked": self.primary_questions_asked,
            "follow_ups_on_current_day": self.follow_ups_on_current_day,
            "covered_days": list(self.covered_days),
            "is_complete": self.is_complete,
            "feedback": self.feedback,
            "current_target_index": self.current_target_index,
            "nonsense_strikes": self.nonsense_strikes,
            "phase": self.phase,
            "last_answer_quality": self.last_answer_quality,
            "interview_notes": self.interview_notes,
            "created_at": self.created_at,
            "last_active_at": self.last_active_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterviewSession':
        sess = cls(data["session_id"], data["raw_candidate"])
        sess.messages = data.get("messages", [])
        sess.questions_asked = data.get("questions_asked", 0)
        sess.primary_questions_asked = data.get("primary_questions_asked", 0)
        sess.follow_ups_on_current_day = data.get("follow_ups_on_current_day", 0)
        sess.covered_days = set(data.get("covered_days", []))
        sess.is_complete = data.get("is_complete", False)
        sess.feedback = data.get("feedback")
        sess.current_target_index = data.get("current_target_index", 0)
        sess.nonsense_strikes = data.get("nonsense_strikes", 0)
        sess.phase = data.get("phase", "INTRO")
        sess.last_answer_quality = data.get("last_answer_quality")
        sess.interview_notes = data.get("interview_notes", "")
        sess.created_at = data.get("created_at", time.time())
        sess.last_active_at = data.get("last_active_at", time.time())
        return sess


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}

    def get_or_create_session(self, session_id: str, candidate_data: Optional[Dict[str, Any]] = None) -> InterviewSession:
        from interview.store import session_store

        if session_id in self._sessions:
            session = self._sessions[session_id]
            if candidate_data and not session.raw_candidate:
                session.raw_candidate = candidate_data
                session.analysis = CandidateAnalyzer.analyze(candidate_data)
            session.touch()
            session_store.save_session(session.to_dict())
            return session

        # Check SQLite store
        stored_dict = session_store.load_session(session_id)
        if stored_dict:
            session = InterviewSession.from_dict(stored_dict)
            if candidate_data and not session.raw_candidate:
                session.raw_candidate = candidate_data
                session.analysis = CandidateAnalyzer.analyze(candidate_data)
            self._sessions[session_id] = session
            session.touch()
            session_store.save_session(session.to_dict())
            return session

        if not candidate_data:
            raise ValueError(f"Session '{session_id}' not found and candidate_data not provided to start session.")

        session = InterviewSession(session_id, candidate_data)
        self._sessions[session_id] = session
        session_store.save_session(session.to_dict())
        return session

    def save_session(self, session: InterviewSession):
        from interview.store import session_store
        session.touch()
        self._sessions[session.session_id] = session
        session_store.save_session(session.to_dict())

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        from interview.store import session_store

        session = self._sessions.get(session_id)
        if not session:
            stored_dict = session_store.load_session(session_id)
            if stored_dict:
                session = InterviewSession.from_dict(stored_dict)
                self._sessions[session_id] = session

        if session:
            session.touch()
            session_store.save_session(session.to_dict())
        return session

    def remove_session(self, session_id: str):
        from interview.store import session_store
        if session_id in self._sessions:
            del self._sessions[session_id]
        session_store.delete_session(session_id)


session_manager = SessionManager()

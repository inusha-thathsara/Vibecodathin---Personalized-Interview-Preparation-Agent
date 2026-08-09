from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class MemberSchema(BaseModel):
    id: str = Field(..., description="Candidate unique ID")
    name: str = Field(..., description="Full candidate name")
    jobRole: str = Field(..., description="Target or current job role")
    yearsExperience: float = Field(0.0, description="Years of experience")
    education: str = Field("", description="Highest education degree/background")

class MissionSchema(BaseModel):
    day: int = Field(..., description="Curriculum day number (1-31)")
    name: Optional[str] = Field(None, description="Mission title/name")
    passed: Optional[bool] = Field(None, description="Whether mission was passed")
    attempts: int = Field(1, description="Number of attempts on this mission")
    skipped: Optional[bool] = Field(False, description="Whether mission was skipped")

class SignalsSchema(BaseModel):
    commitDays: Union[int, List[int]] = Field(0, description="Days or count of code commits")
    missionsCompleted: Union[int, List[int]] = Field(0, description="Days or count of completed missions")
    missionsFirstTry: Union[int, List[int]] = Field(0, description="Days or count passed on first try")

class CandidateSchema(BaseModel):
    member: MemberSchema
    missions: List[MissionSchema] = Field(default_factory=list)
    signals: SignalsSchema = Field(default_factory=SignalsSchema)

class TopicScore(BaseModel):
    day: int = Field(..., description="Curriculum day number")
    title: str = Field(..., description="Day title")
    score: int = Field(..., description="Score 1-10")
    note: str = Field("", description="Evaluation note for this topic")
    tools: Optional[List[str]] = Field(default_factory=list, description="Associated topic tools")

class FeedbackSchema(BaseModel):
    summary: str = Field(..., description="Detailed 2-3 sentence overall evaluation")
    strengths: List[str] = Field(default_factory=list, description="List of technical strengths")
    gaps: List[str] = Field(default_factory=list, description="List of identified knowledge gaps")
    next: List[str] = Field(default_factory=list, description="List of recommended next steps")
    topic_scores: List[TopicScore] = Field(default_factory=list, description="Additive per-topic scores")
    evidence: List[str] = Field(default_factory=list, description="Quoted evidence from candidate responses")

class InterviewMeta(BaseModel):
    phase: str = Field("CORE", description="Interview phase (INTRO, CORE, FOLLOW_UP, WRAP_UP)")
    primary_questions: int = Field(0, description="Number of primary curriculum questions asked")
    days_covered: List[int] = Field(default_factory=list, description="List of curriculum day numbers covered")
    current_day: int = Field(7, description="Current target curriculum day")
    current_title: str = Field("", description="Current target curriculum topic title")
    llm_provider: Optional[str] = Field("ollama", description="Active LLM provider (ollama, gemini, mock)")
    llm_model: Optional[str] = Field("gemma3:1b", description="Exact LLM model loaded and executing")
    llm_latency_ms: Optional[float] = Field(0.0, description="Model generation response time in milliseconds")
    llm_status: Optional[str] = Field("success", description="Status of LLM call (success, fallback, error)")
    llm_fallback: Optional[bool] = Field(False, description="Whether fallback model was used")

class InterviewRequest(BaseModel):
    sessionId: str = Field(..., description="Unique interview session ID")
    candidate: Optional[CandidateSchema] = Field(None, description="Candidate profile data (sent on initial request)")
    message: Optional[str] = Field(None, description="Candidate answer message (sent on subsequent requests)")
    endEarly: Optional[bool] = Field(False, description="Flag to terminate the interview session immediately")

class InterviewResponse(BaseModel):
    reply: str = Field(..., description="Interviewer reply text")
    done: bool = Field(False, description="Whether the interview is complete")
    feedback: Optional[FeedbackSchema] = Field(None, description="Structured feedback returned when done is true")
    meta: Optional[InterviewMeta] = Field(None, description="Current interview progress metadata")

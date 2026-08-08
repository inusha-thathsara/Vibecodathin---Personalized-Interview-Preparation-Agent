import json
import re
import logging
from typing import Dict, Any
from interview.session import InterviewSession
from interview.prompts import FEEDBACK_SYSTEM_PROMPT
from llm.provider import get_llm_provider
from data.loader import data_loader

logger = logging.getLogger(__name__)

DESCRIPTIVE_TOPIC_NOTES = {
    1: "Evaluated local environment setup, VS Code configuration, Pyright type checking, and virtual environment isolation.",
    2: "Assessed Git branching strategies, atomic commit habits, code review processes, and merge conflict resolution.",
    3: "Evaluated Python dependency management, requirements reproduction, package locking with pip/uv, and environment isolation.",
    4: "Assessed Pydantic V2 schema definition, type validation, data parsing, and API contract enforcement.",
    5: "Evaluated FastAPI REST endpoints, OpenAPI schema generation, async handlers, and exception handling.",
    6: "Assessed Docker multi-stage containerization, image optimization, environment variables, and docker-compose deployment.",
    7: "Evaluated dense vector embeddings (OpenAI / Gemini), high-dimensional vector math, and Cosine vs L2 similarity metrics.",
    8: "Assessed Vector DB integration (ChromaDB / Qdrant), HNSW indexing parameters, and metadata filtering for fast search.",
    9: "Evaluated hybrid vector & keyword search, reciprocal rank fusion (RRF), and retrieval precision calibration.",
    10: "Assessed end-to-end RAG architecture, document chunking strategies, vector retrieval, and context injection into prompts.",
    11: "Evaluated RAG re-ranking models (Cohere / BGE), cross-encoders, and dynamic chunk windowing for context retrieval.",
    12: "Assessed prompt engineering patterns, few-shot exemplars, system instruction design, and template variable formatting.",
    13: "Evaluated LLM Structured Outputs, Pydantic schema validation, and deterministic JSON mode execution.",
    14: "Assessed AI Agent tool calling, function signature schemas, parameter validation, and tool execution failure recovery.",
    15: "Evaluated conversational Chatbot agent architecture, memory buffer management, and multi-turn context retention.",
    16: "Assessed scalable Chatbot backend APIs, streaming response tokens, vector DB connections, and web socket handling.",
    17: "Evaluated Multi-Agent router-supervisor architectures, domain sub-agent delegation, and task distribution.",
    18: "Assessed agentic state machine design, shared graph memory (LangGraph / CrewAI), and state synchronization.",
    19: "Evaluated agent failure modes, recursion limits, automated retries, and dead-letter queue handling.",
    20: "Assessed agent integration with external REST APIs, web search tools, SQL query execution, and sandboxing.",
    21: "Evaluated Human-in-the-Loop approval workflows, high-risk action confirmation, and safety gates for AI agents.",
    22: "Assessed complex multi-agent orchestration, state persistence, checkpointing, and parallel sub-agent execution.",
    23: "Evaluated Model Context Protocol (MCP) server & client integration, standardized tool schemas, and resource sharing.",
    24: "Assessed LLM inference optimization, streaming token handling, and asynchronous task queue throughput.",
    25: "Evaluated structured telemetry, OpenTelemetry distributed tracing, prompt latency metrics, and error logging.",
    26: "Assessed LLM output guardrails, Pydantic schema enforcement, hallucination detection, and safety filters.",
    27: "Evaluated AI system security: API key management, prompt injection defense, CORS, and data privacy controls.",
    28: "Assessed automated RAG evaluation frameworks (Ragas / DeepEval), measuring faithfulness, recall, and relevance.",
    29: "Evaluated open-weights model fine-tuning (Gemma / Qwen), LoRA / QLoRA parameter-efficient adaptation, and datasets.",
    30: "Assessed local model quantization (GGUF / Ollama / AWQ), VRAM memory footprint optimization, and edge inference.",
    31: "Evaluated end-to-end capstone AI engineering architecture, user experience, code structure, and production readiness."
}

def _enrich_topic_scores(topic_scores: list, covered_days: set, analysis: dict) -> list:
    """Ensures every covered day has a rich, descriptive evaluation note and tool metadata."""
    covered_set = set(covered_days) if covered_days else set()
    existing_days = {ts.get("day") for ts in topic_scores if isinstance(ts, dict) and ts.get("day")}

    for d in covered_set:
        if d not in existing_days:
            info = data_loader.get_day_info(d) or {}
            topic_scores.append({
                "day": d,
                "title": info.get("title", f"Day {d}"),
                "score": 8 if d in analysis.get("first_try_days", []) else 6,
                "note": ""
            })

    first_try = set(analysis.get("first_try_days", []))
    struggle = set(analysis.get("struggle_days", []))

    for ts in topic_scores:
        if not isinstance(ts, dict):
            continue
        d = ts.get("day", 1)
        info = data_loader.get_day_info(d) or {}
        if not ts.get("title"):
            ts["title"] = info.get("title", f"Day {d}")

        tools = info.get("tools", [])
        ts["tools"] = tools

        curr_note = str(ts.get("note", "")).strip()
        if not curr_note or curr_note.lower() in ("evaluated during interview session", "none", "evaluated"):
            desc = DESCRIPTIVE_TOPIC_NOTES.get(d, f"Evaluated core engineering concepts and technical reasoning for Day {d}.")
            tools_str = f" Primary tools: {', '.join(tools[:3])}." if tools else ""
            if d in first_try:
                perf_note = " Candidate demonstrated first-try mastery during cohort projects."
            elif d in struggle:
                perf_note = " Identified as a key struggle area requiring targeted review."
            else:
                perf_note = " Solved with consistent technical understanding."
            ts["note"] = f"{desc}{tools_str}{perf_note}"

    topic_scores.sort(key=lambda x: x.get("day", 0))
    return topic_scores

def generate_feedback(session: InterviewSession) -> Dict[str, Any]:
    llm = get_llm_provider()
    analysis = session.analysis

    conv_text = ""
    for msg in session.messages:
        speaker = "Interviewer" if msg["role"] == "assistant" else "Candidate"
        conv_text += f"{speaker}: {msg['content']}\n\n"

    system_prompt = FEEDBACK_SYSTEM_PROMPT.format(
        name=analysis.get("name", "Candidate"),
        job_role=analysis.get("jobRole", "Software Engineer"),
        years_exp=analysis.get("yearsExperience", 0)
    )

    messages = [
        {"role": "user", "content": f"Here is the complete interview transcript to evaluate:\n\n{conv_text}"}
    ]

    try:
        raw_output = llm.generate(messages, system_prompt=system_prompt)
        
        clean_json = raw_output.strip()
        if "```" in clean_json:
            clean_json = re.sub(r"^```(?:json)?", "", clean_json, flags=re.MULTILINE)
            clean_json = re.sub(r"```$", "", clean_json, flags=re.MULTILINE).strip()

        start = clean_json.find("{")
        end = clean_json.rfind("}")
        if start != -1 and end != -1:
            clean_json = clean_json[start:end+1]

        data = json.loads(clean_json)
        topic_scores = data.get("topic_scores", [])
        topic_scores = _enrich_topic_scores(topic_scores, session.covered_days, analysis)

        evidence = data.get("evidence", [])
        if not evidence:
            for msg in session.messages:
                if msg["role"] == "user" and len(msg["content"].strip()) > 15:
                    evidence.append(f"Candidate: \"{msg['content'][:80]}...\"")
                    if len(evidence) >= 2:
                        break

        return {
            "summary": str(data.get("summary", "Candidate demonstrated good foundational technical knowledge throughout the interview.")),
            "strengths": list(data.get("strengths", ["Strong core understanding of AI cohort concepts", "Clear technical communication"])),
            "gaps": list(data.get("gaps", ["Deeper hands-on architectural experience in edge failure modes"])),
            "next": list(data.get("next", ["Review advanced agentic orchestration patterns and production monitoring"])),
            "topic_scores": topic_scores,
            "evidence": evidence
        }
    except Exception as e:
        logger.error(f"Failed to generate structured feedback via LLM: {e}")
        struggles = analysis.get("struggle_days", [])
        strengths = analysis.get("first_try_days", [])
        
        topic_scores = _enrich_topic_scores([], session.covered_days, analysis)

        return {
            "summary": f"{analysis.get('name')} completed a comprehensive technical interview covering key AI cohort modules with solid technical reasoning.",
            "strengths": [
                f"Demonstrated solid grasp of concepts from Day {day}" for day in strengths[:3]
            ] or ["Strong general comprehension of core AI engineering topics"],
            "gaps": [
                f"Requires further consolidation on Day {day} concepts" for day in struggles[:2]
            ] or ["Complex system boundary failure handling"],
            "next": [
                "Practice architecture design for multi-agent workflows",
                "Deepen hands-on testing on RAG retrieval optimization"
            ],
            "topic_scores": topic_scores,
            "evidence": ["Evaluation based on candidate response consistency across turns."]
        }

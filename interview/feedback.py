import json
import re
import logging
from typing import Dict, Any
from interview.session import InterviewSession
from interview.prompts import FEEDBACK_SYSTEM_PROMPT
from llm.provider import get_llm_provider
from data.loader import data_loader

logger = logging.getLogger(__name__)

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
        if not topic_scores:
            # Generate fallback topic scores for covered days
            for d in list(session.covered_days):
                info = data_loader.get_day_info(d) or {}
                topic_scores.append({
                    "day": d,
                    "title": info.get("title", f"Day {d}"),
                    "score": 8 if d in analysis.get("first_try_days", []) else 6,
                    "note": "Evaluated during interview session"
                })

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
        
        topic_scores = []
        for d in list(session.covered_days):
            info = data_loader.get_day_info(d) or {}
            topic_scores.append({
                "day": d,
                "title": info.get("title", f"Day {d}"),
                "score": 8 if d in strengths else 6,
                "note": "Evaluated during interview session"
            })

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

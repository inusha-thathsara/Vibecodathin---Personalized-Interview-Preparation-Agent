import json
import logging
import re
from typing import Dict, Any, List
from llm.provider import get_llm_provider

logger = logging.getLogger(__name__)

class AnswerEvaluator:
    @staticmethod
    def evaluate(target_day: int, target_title: str, candidate_answer: str) -> Dict[str, Any]:
        """
        Evaluates the candidate's answer for accuracy, technical depth, and completeness.
        Returns a dict: {"quality": "accurate"|"partial"|"incorrect"|"off_topic"|"nonsense", "key_points": [], "gaps": []}
        """
        if not candidate_answer or len(candidate_answer.strip()) < 4:
            return {"quality": "nonsense", "key_points": [], "gaps": ["No substantive response provided"]}

        llm = get_llm_provider()
        prompt = f"""You are a technical evaluation assistant. Evaluate the candidate's answer for Day {target_day} ({target_title}).

Candidate Answer: "{candidate_answer}"

Return ONLY a JSON object with no markdown syntax outside:
{{
  "quality": "accurate" | "partial" | "incorrect" | "off_topic" | "nonsense",
  "key_points": ["point 1"],
  "gaps": ["gap 1"]
}}
"""

        try:
            resp = llm.generate([{"role": "user", "content": prompt}], system_prompt="You are a strict JSON answer evaluator.")
            # Extract JSON
            cleaned = resp.strip()
            if "```" in cleaned:
                cleaned = re.sub(r"```json\s*", "", cleaned)
                cleaned = re.sub(r"```\s*", "", cleaned)
            data = json.loads(cleaned.strip())
            quality = data.get("quality", "partial").lower()
            if quality not in ("accurate", "partial", "incorrect", "off_topic", "nonsense"):
                quality = "partial"
            return {
                "quality": quality,
                "key_points": data.get("key_points", []),
                "gaps": data.get("gaps", [])
            }
        except Exception as e:
            logger.warning(f"Evaluator LLM error ({e}), using heuristic fallback")
            # Heuristic fallback based on length and keywords
            text = candidate_answer.lower()
            if len(text.split()) > 15 and any(w in text for w in ["vector", "embedding", "rag", "model", "data", "api", "query", "pipeline", "agent", "prompt", "token", "layer"]):
                return {"quality": "accurate", "key_points": ["Addressed technical subject"], "gaps": []}
            elif len(text.split()) >= 5:
                return {"quality": "partial", "key_points": ["Provided brief answer"], "gaps": ["May lack implementation depth"]}
            else:
                return {"quality": "incorrect", "key_points": [], "gaps": ["Response was too brief"]}

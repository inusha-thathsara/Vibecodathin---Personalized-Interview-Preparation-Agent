import logging
import json
import time
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import config

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        pass

    def generate_with_metadata(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        text = self.generate(messages, system_prompt)
        return text, {"provider": "unknown", "model": "unknown", "latency_ms": 0.0, "status": "success", "fallback": False}

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL_NAME

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        text, _ = self.generate_with_metadata(messages, system_prompt)
        return text

    def generate_with_metadata(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        t0 = time.perf_counter()
        if not self.api_key:
            logger.warning("[GEMINI DEBUG] GEMINI_API_KEY not set. Falling back to Ollama...")
            return OllamaProvider().generate_with_metadata(messages, system_prompt)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [msg["content"]]})

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt if system_prompt else None
            )

            response = model.generate_content(contents)
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)

            if response and response.text:
                res_text = response.text.strip()
                logger.info(f"[GEMINI DEBUG SUCCESS] Model '{self.model_name}' responded in {latency_ms}ms")
                return res_text, {
                    "provider": "gemini",
                    "model": self.model_name,
                    "latency_ms": latency_ms,
                    "status": "success",
                    "fallback": False
                }
            
            return "I apologize, but I could not generate a response.", {
                "provider": "gemini",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "status": "empty",
                "fallback": False
            }
        except Exception as e:
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            logger.warning(f"[GEMINI DEBUG ERROR] Gemini error after {latency_ms}ms ({e}). Attempting Ollama / Mock fallback...")
            return OllamaProvider().generate_with_metadata(messages, system_prompt)

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = None, model_name: str = None):
        self.base_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or config.OLLAMA_MODEL

    def _get_available_model(self) -> Tuple[str, List[str]]:
        """Query Ollama for available installed models, returning (best_match, all_installed)."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                if not models:
                    return self.model_name, []
                
                for m in models:
                    if self.model_name == m or self.model_name in m:
                        return m, models
                
                preferred = ["gemma3:1b", "qwen2.5", "qwen3:4b", "gemma4:e2b", "gemma4:latest", "gemma4:e4b", "moondream:latest"]
                for p in preferred:
                    if p in models:
                        return p, models
                
                return models[0], models
        except Exception as e:
            logger.warning(f"[OLLAMA DEBUG] Could not list Ollama tags: {e}")
            return self.model_name, []

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        text, _ = self.generate_with_metadata(messages, system_prompt)
        return text

    def generate_with_metadata(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        t0 = time.perf_counter()
        active_model, all_models = self._get_available_model()
        logger.info(f"[OLLAMA DEBUG TRACE] Ollama server: {self.base_url} | Installed models: {all_models}")

        # Build prioritized list of candidate models: active_model first, then lightweight stable models
        preferred_fallback_order = ["gemma3:1b", "qwen3:4b", "gemma4:e2b", "qwen2.5", "moondream:latest"]
        candidate_models = [active_model]
        for pref in preferred_fallback_order:
            if pref in all_models and pref not in candidate_models:
                candidate_models.append(pref)
        for m in all_models:
            if m not in candidate_models:
                candidate_models.append(m)

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        url = f"{self.base_url}/api/chat"
        last_error = None

        for model_to_try in candidate_models:
            logger.info(f"[OLLAMA DEBUG TRACE] Executing inference request on model '{model_to_try}'...")
            payload = {
                "model": model_to_try,
                "messages": formatted_messages,
                "stream": False
            }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"}
            )

            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                    result = json.loads(response.read().decode("utf-8"))
                    res_content = result.get("message", {}).get("content", "").strip()
                    if res_content:
                        logger.info(f"[OLLAMA DEBUG SUCCESS] Model '{model_to_try}' responded in {latency_ms}ms ({len(res_content)} chars)")
                        return res_content, {
                            "provider": "ollama",
                            "model": model_to_try,
                            "latency_ms": latency_ms,
                            "status": "success",
                            "fallback": False
                        }
            except Exception as e:
                last_error = e
                logger.warning(f"[OLLAMA DEBUG WARNING] Model '{model_to_try}' failed ({e}). Trying next model...")

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.warning(f"[OLLAMA DEBUG ERROR] All Ollama candidate models failed after {latency_ms}ms ({last_error}). Falling back to OfflineMockProvider...")
        mock_text, mock_meta = OfflineMockProvider().generate_with_metadata(messages, system_prompt)
        mock_meta["fallback"] = True
        mock_meta["model"] = f"mock (fallback from ollama: {last_error})"
        return mock_text, mock_meta

class OfflineMockProvider(LLMProvider):
    """Offline mock provider for deterministic tests and fallback."""
    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        text, _ = self.generate_with_metadata(messages, system_prompt)
        return text

    def generate_with_metadata(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        t0 = time.perf_counter()
        user_msgs = [m for m in messages if m.get("role") == "user"]
        turn_count = len(user_msgs)
        last_user_msg = user_msgs[-1].get("content", "") if user_msgs else ""

        target_title = "Embeddings & Vector Search"
        candidate_name = "Candidate"
        if system_prompt:
            if "Day" in system_prompt:
                try:
                    for line in system_prompt.splitlines():
                        if "Curriculum Focus:" in line or "Day " in line:
                            target_title = line.strip()
                            break
                except Exception:
                    pass

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.info(f"[MOCK DEBUG SUCCESS] OfflineMockProvider generated response in {latency_ms}ms")

        # 1. Opening Question (Turn 0 or 1)
        if turn_count <= 1 or not last_user_msg or "start" in last_user_msg.lower():
            text = f"Welcome {candidate_name}! Let's begin your technical interview focusing on {target_title}.\n\nCould you explain the core concepts of this topic and how you applied them during your cohort projects?"
        elif "embedding" in last_user_msg.lower() or "vector" in last_user_msg.lower():
            text = "That's a solid explanation of vector representations. Following up on that, when building an end-to-end RAG system, how do you handle metadata filtering alongside vector similarity search to optimize retrieval precision?"
        elif "rag" in last_user_msg.lower() or "retrieval" in last_user_msg.lower() or "filter" in last_user_msg.lower():
            text = "Great point on hybrid search. In a Multi-Agent architecture using frameworks like LangGraph or CrewAI, how do you prevent cascading failure loops between autonomous sub-agents?"
        elif "monitor" in last_user_msg.lower() or "reliability" in last_user_msg.lower() or "pydantic" in last_user_msg.lower() or "docker" in last_user_msg.lower():
            text = "Excellent emphasis on schema validation and containerization! How do you handle dead-letter queues, automated retries, and data drift detection when scaling this pipeline to millions of daily requests?"
        elif turn_count == 2:
            text = "Thank you for that explanation! How would you monitor and ensure high operational reliability when deploying this pipeline into production?"
        elif turn_count == 3:
            text = "Impressive operational insights. How do you approach API rate limiting, asynchronous task queues, and state recovery during unexpected cloud infrastructure outages?"
        elif turn_count == 4:
            text = "That covers the architecture well. Looking at performance optimization, how do you evaluate model latency vs. output accuracy trade-offs when selecting between large foundational models and quantized edge models?"
        elif turn_count == 5:
            text = "Great discussion! To wrap up our technical session, what key lesson or architectural refactoring from your 31-day cohort experience are you most proud of implementing?"
        else:
            text = f"Thank you for sharing those technical insights! That concludes our core interview questions for {target_title}. I am preparing your evaluation review now."

        return text, {
            "provider": "mock",
            "model": "offline-mock-engine",
            "latency_ms": latency_ms,
            "status": "success",
            "fallback": False
        }

class AutoLLMProvider(LLMProvider):
    def __init__(self):
        self.mock = OfflineMockProvider()

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        gemini_key = config.GEMINI_API_KEY or ""
        
        if gemini_key:
            try:
                gemini = GeminiProvider(api_key=gemini_key)
                res = gemini.generate(messages, system_prompt)
                if res and "could not generate a response" not in res.lower():
                    return res
            except Exception as e:
                logger.warning(f"Gemini API error ({e}), attempting fallback...")

        try:
            ollama = OllamaProvider()
            res = ollama.generate(messages, system_prompt)
            if res and len(res.strip()) > 0:
                return res
        except Exception as e:
            logger.warning(f"Ollama error ({e}), falling back to Offline Mock Provider...")

        return self.mock.generate(messages, system_prompt)

def get_llm_provider() -> LLMProvider:
    provider = config.LLM_PROVIDER
    if config.APP_ENV == "test" or provider == "mock":
        return OfflineMockProvider()
    elif provider == "gemini":
        return GeminiProvider()
    elif provider == "ollama":
        return OllamaProvider()
    elif provider == "auto":
        return AutoLLMProvider()
    
    logger.warning(f"Unknown LLM_PROVIDER '{provider}', using default environment provider.")
    if config.APP_ENV == "production":
        return GeminiProvider()
    return OllamaProvider()

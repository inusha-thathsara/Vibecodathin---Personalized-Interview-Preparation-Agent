import logging
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL_NAME

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)

        # Build contents from messages
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt if system_prompt else None
        )

        response = model.generate_content(contents)
        if response and response.text:
            return response.text.strip()
        return "I apologize, but I could not generate a response."

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = None, model_name: str = None):
        self.base_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or config.OLLAMA_MODEL

    def _get_available_model(self) -> str:
        """Query Ollama for available installed models, returning best match."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                if not models:
                    return self.model_name
                
                for m in models:
                    if self.model_name == m or self.model_name in m:
                        return m
                
                preferred = ["gemma3:1b", "qwen3:4b", "gemma4:e2b", "gemma4:latest", "gemma4:e4b", "moondream:latest", "qwen2.5"]
                for p in preferred:
                    if p in models:
                        return p
                
                return models[0]
        except Exception as e:
            logger.warning(f"Could not list Ollama tags: {e}")
            return self.model_name

    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        active_model = self._get_available_model()
        logger.info(f"Ollama using model: {active_model}")

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": active_model,
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
                result = json.loads(response.read().decode("utf-8"))
                return result.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.warning(f"Ollama execution error: {e}")
            raise RuntimeError(f"Ollama execution error: {e}")

class OfflineMockProvider(LLMProvider):
    """Offline mock provider for deterministic tests and fallback."""
    def generate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

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

        if not last_user_msg or "start" in last_user_msg.lower():
            return f"Welcome {candidate_name}! Let's begin your technical interview focusing on {target_title}.\n\nCould you explain the core concepts of this topic and how you applied them during your cohort projects?"
        elif "embedding" in last_user_msg.lower() or "vector" in last_user_msg.lower():
            return "That's a solid explanation. Following up on that, when building an end-to-end RAG system, how do you handle metadata filtering alongside vector similarity search to optimize retrieval precision?"
        elif "rag" in last_user_msg.lower() or "retrieval" in last_user_msg.lower() or "filter" in last_user_msg.lower():
            return "Great point on hybrid search. In a Multi-Agent architecture using frameworks like LangGraph or CrewAI, how do you prevent cascading failure loops between autonomous sub-agents?"
        else:
            return f"Thank you for that response! How would you monitor and ensure high reliability when deploying this pipeline into production?"

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

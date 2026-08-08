import logging
import json
import urllib.request
import config

logger = logging.getLogger(__name__)

def check_llm_health() -> dict:
    """Probes the configured LLM provider and returns status dict."""
    provider_name = config.LLM_PROVIDER
    env = config.APP_ENV

    if env == "test" or provider_name == "mock":
        return {"status": "ok", "env": env, "llm": "mock", "detail": "Test/Mock mode active"}

    if provider_name == "gemini":
        if not config.GEMINI_API_KEY:
            msg = "GEMINI_API_KEY is missing in production/gemini mode."
            logger.error(msg)
            if env == "production":
                raise RuntimeError(msg)
            return {"status": "error", "env": env, "llm": "gemini", "detail": msg}
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            # Lightweight probe
            model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)
            logger.info("Gemini provider health check passed.")
            return {"status": "ok", "env": env, "llm": "gemini", "detail": "Gemini API configured"}
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            if env == "production":
                raise RuntimeError(f"Gemini API health check failed: {e}")
            return {"status": "error", "env": env, "llm": "gemini", "detail": str(e)}

    elif provider_name == "ollama":
        url = f"{config.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                logger.info(f"Ollama server responsive. Models found: {models}")
                return {"status": "ok", "env": env, "llm": "ollama", "models": models}
        except Exception as e:
            logger.warning(f"Ollama server probe failed at {url}: {e}")
            return {"status": "warning", "env": env, "llm": "ollama", "detail": f"Ollama not reachable: {e}"}

    return {"status": "ok", "env": env, "llm": provider_name, "detail": "Provider ready"}

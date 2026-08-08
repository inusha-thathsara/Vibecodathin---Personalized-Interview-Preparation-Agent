import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

BASE_DIR = Path(__file__).parent
CANDIDATES_FILE = BASE_DIR / "candidates.json"
CURRICULUM_FILE = BASE_DIR / "curriculum.json"
DATA_DIR = BASE_DIR / "data"
SESSIONS_DB_FILE = DATA_DIR / "sessions.db"
EMBEDDING_CACHE_FILE = DATA_DIR / "embedding_cache.json"

APP_ENV = os.getenv("APP_ENV", "development").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:latest")

# Environment-aware LLM provider default
_default_provider = "ollama" if APP_ENV == "development" else "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", _default_provider).lower()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

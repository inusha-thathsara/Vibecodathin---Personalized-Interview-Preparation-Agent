import json
import logging
from typing import List, Dict, Any
from pathlib import Path
import config
from data.loader import data_loader
from rag.embeddings import get_embedding

logger = logging.getLogger(__name__)

class CurriculumIndexer:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def initialize_index(self):
        """
        Loads curriculum chunks and initializes embeddings from embedding_cache.json
        or generates them live if in production with Gemini.
        """
        curriculum = data_loader.get_curriculum()
        chunks = []

        for day_item in curriculum:
            day = day_item.get("day")
            title = day_item.get("title", "")
            tools = ", ".join(day_item.get("tools", []))
            objectives = "; ".join(day_item.get("objectives", []))
            content = f"Day {day}: {title}. Tools: {tools}. Objectives: {objectives}"

            chunks.append({
                "day": day,
                "title": title,
                "content": content,
                "embedding": []
            })

        # Check for pre-built embedding cache
        cache_file = config.EMBEDDING_CACHE_FILE
        cache_map = {}
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    for item in cache_data:
                        cache_map[item["day"]] = item.get("embedding", [])
                logger.info(f"Loaded {len(cache_map)} pre-computed embeddings from cache.")
            except Exception as e:
                logger.warning(f"Could not read embedding cache: {e}")

        # Fill missing embeddings if Gemini key is available
        needs_save = False
        for c in chunks:
            day = c["day"]
            if day in cache_map and cache_map[day]:
                c["embedding"] = cache_map[day]
            elif config.GEMINI_API_KEY and config.LLM_PROVIDER == "gemini":
                emb = get_embedding(c["content"])
                if emb:
                    c["embedding"] = emb
                    needs_save = True

        self.documents = chunks
        logger.info(f"Curriculum Index initialized with {len(self.documents)} documents.")

        # Persist updated cache if generated
        if needs_save and not cache_file.exists():
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.documents, f, indent=2)
                logger.info("Saved generated embeddings to cache file.")
            except Exception as e:
                logger.warning(f"Failed to save embedding cache: {e}")

curriculum_indexer = CurriculumIndexer()

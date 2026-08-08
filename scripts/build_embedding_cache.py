"""
One-time script to generate embedding_cache.json for local dev/testing without needing live Gemini key at runtime.
Usage: python scripts/build_embedding_cache.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import config
from data.loader import data_loader
from rag.embeddings import get_embedding

def build_cache():
    if not config.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set in .env. Cannot generate embeddings.")
        sys.exit(1)

    curriculum = data_loader.get_curriculum()
    cache_data = []

    print(f"Generating embeddings for {len(curriculum)} curriculum days...")
    for day_item in curriculum:
        day = day_item.get("day")
        title = day_item.get("title", "")
        tools = ", ".join(day_item.get("tools", []))
        objectives = "; ".join(day_item.get("objectives", []))
        content = f"Day {day}: {title}. Tools: {tools}. Objectives: {objectives}"

        print(f"Embedding Day {day}: {title}...")
        emb = get_embedding(content)
        cache_data.append({
            "day": day,
            "title": title,
            "content": content,
            "embedding": emb
        })

    output_path = config.EMBEDDING_CACHE_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

    print(f"Successfully saved embedding cache to {output_path}")

if __name__ == "__main__":
    build_cache()

import logging
from typing import List, Dict, Any
from rag.indexer import curriculum_indexer
from rag.embeddings import get_embedding, cosine_similarity

logger = logging.getLogger(__name__)

class CurriculumRetriever:
    @staticmethod
    def retrieve_context(day: int, query: str = "", top_k: int = 2) -> str:
        """
        Retrieves relevant curriculum context chunks matching the current day and query.
        Returns a formatted markdown string for system prompt injection.
        """
        docs = curriculum_indexer.documents
        if not docs:
            return ""

        # Find target day document
        day_doc = next((d for d in docs if d["day"] == day), None)
        relevant_docs = []

        if day_doc:
            relevant_docs.append(day_doc)

        # Retrieve top query matches if query provided
        if query and len(query.strip()) > 3:
            query_emb = get_embedding(query)
            
            scored_docs = []
            for d in docs:
                if d["day"] == day:
                    continue  # Already added
                score = 0.0
                if query_emb and d.get("embedding"):
                    score = cosine_similarity(query_emb, d["embedding"])
                else:
                    # Keyword overlap fallback
                    q_words = set(query.lower().split())
                    content_words = set(d["content"].lower().split())
                    score = len(q_words.intersection(content_words)) / max(1, len(q_words))

                scored_docs.append((score, d))

            scored_docs.sort(key=lambda x: x[0], reverse=True)
            for score, d in scored_docs[:top_k - 1]:
                if score > 0.05:
                    relevant_docs.append(d)

        if not relevant_docs:
            return ""

        lines = ["### Relevant Curriculum Context (RAG):"]
        for d in relevant_docs:
            lines.append(f"- **Day {d['day']} ({d['title']})**: {d['content']}")

        return "\n".join(lines)

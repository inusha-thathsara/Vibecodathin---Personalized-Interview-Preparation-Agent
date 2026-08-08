import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.indexer import curriculum_indexer
from rag.retriever import CurriculumRetriever

def test_rag_retrieval():
    curriculum_indexer.initialize_index()
    assert len(curriculum_indexer.documents) > 0

    context = CurriculumRetriever.retrieve_context(day=7, query="vector similarity embeddings", top_k=2)
    assert "Day 7" in context or "Embeddings" in context

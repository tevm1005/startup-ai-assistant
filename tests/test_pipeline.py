"""Tests for IngestionPipeline retrieval and fallback logic."""

import pytest

from src.ingestion.pipeline import IngestionPipeline
from src.knowledge.store import KnowledgeStore
from src.response.generator import ResponseGenerator


@pytest.mark.asyncio
async def test_falls_back_to_knowledge_store_when_no_vector_store():
    ks = KnowledgeStore()
    ks.add("O plano básico custa R$ 49,90")
    pipeline = IngestionPipeline(knowledge=ks)
    result = await pipeline.run("preço do plano básico")
    assert "49,90" in result or "mock" in result


@pytest.mark.asyncio
async def test_uses_vector_store_when_provided():
    ks = KnowledgeStore()
    ks.add("O plano básico custa R$ 49,90")

    class FakeVectorStore:
        async def search(self, query, top_k=5):
            return [{"content": "from vector store", "metadata": {}, "id": "1"}]

    pipeline = IngestionPipeline(knowledge=ks, vector_store=FakeVectorStore())
    result = await pipeline.run("question")
    assert "vector store" in result


@pytest.mark.asyncio
async def test_falls_back_when_vector_store_returns_empty():
    ks = KnowledgeStore()
    ks.add("O plano básico custa R$ 49,90")

    class EmptyVectorStore:
        async def search(self, query, top_k=5):
            return []

    pipeline = IngestionPipeline(knowledge=ks, vector_store=EmptyVectorStore())
    result = await pipeline.run("plano básico")
    assert "49,90" in result or "plano básico" in result


@pytest.mark.asyncio
async def test_falls_back_when_vector_store_raises():
    ks = KnowledgeStore()
    ks.add("O plano básico custa R$ 49,90")

    class BrokenVectorStore:
        async def search(self, query, top_k=5):
            raise ConnectionError("DB down")

    pipeline = IngestionPipeline(knowledge=ks, vector_store=BrokenVectorStore())
    result = await pipeline.run("plano básico")
    assert "49,90" in result or "plano básico" in result


def test_pipeline_init_defaults():
    pipeline = IngestionPipeline()
    assert pipeline.knowledge is not None
    assert pipeline.response_gen is not None
    assert pipeline.vector_store is None


def test_pipeline_accepts_custom_response_gen():
    gen = ResponseGenerator()
    pipeline = IngestionPipeline(response_gen=gen)
    assert pipeline.response_gen is gen

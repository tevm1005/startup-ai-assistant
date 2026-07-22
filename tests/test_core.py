"""Core interfaces and types smoke tests."""

import pytest

from src.core.types import Platform, MessageDirection, MessageStatus


def test_enums_have_expected_values():
    assert Platform.WHATSAPP.value == "whatsapp"
    assert MessageDirection.INBOUND.value == "inbound"
    assert MessageStatus.PENDING.value == "pending"


@pytest.mark.asyncio
async def test_response_generator_mock():
    from src.response.generator import ResponseGenerator

    gen = ResponseGenerator()
    result = await gen.generate("what is the price?", [{"content": "R$ 49,90"}])
    assert "mock response" in result
    assert "what is the price?" in result


@pytest.mark.asyncio
async def test_embedding_client_mock():
    from src.llm.embeddings import EmbeddingClient

    ec = EmbeddingClient()
    vec = await ec.embed("test text")
    assert len(vec) == 768
    assert all(isinstance(v, float) for v in vec)


def test_knowledge_store_search():
    from src.knowledge.store import KnowledgeStore

    ks = KnowledgeStore()
    ks.add("O plano básico custa R$ 49,90")
    ks.add("Suporte 24 horas para enterprise")

    results = ks.search("plano básico")
    assert len(results) == 1
    assert "básico" in results[0]["content"]


@pytest.mark.asyncio
async def test_ingestion_pipeline_mock():
    from src.knowledge.store import KnowledgeStore
    from src.ingestion.pipeline import IngestionPipeline

    ks = KnowledgeStore()
    ks.add("O plano básico custa R$ 49,90")
    pipeline = IngestionPipeline(knowledge=ks)

    answer = await pipeline.run("qual o preço do plano básico?")
    assert "49,90" in answer or "mock response" in answer

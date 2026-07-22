"""Tests for LLMClient and EmbeddingClient mock modes."""

import pytest

from src.llm.client import LLMClient
from src.llm.embeddings import EmbeddingClient


def test_mock_response_contains_model_name():
    client = LLMClient(model="test-model")
    result = client._mock("question", [])
    assert "[test-model" in result


def test_mock_response_includes_context():
    client = LLMClient()
    result = client._mock("question", [{"content": "some context"}])
    assert "some context" in result
    assert "question" in result


def test_mock_response_no_context():
    client = LLMClient()
    result = client._mock("question", [])
    assert "Context used:" not in result


def test_mock_response_truncates_long_context():
    client = LLMClient()
    long = [{"content": f"entry {i} " * 50} for i in range(5)]
    result = client._mock("q", long)
    for i in range(1, 4):
        assert f"{i}." in result


@pytest.mark.asyncio
async def test_embedding_dimension():
    ec = EmbeddingClient()
    vec = await ec.embed("test")
    assert len(vec) == 768


@pytest.mark.asyncio
async def test_embedding_deterministic():
    ec = EmbeddingClient()
    a = await ec.embed("same text")
    b = await ec.embed("same text")
    assert a == b


@pytest.mark.asyncio
async def test_embedding_different_for_different_inputs():
    ec = EmbeddingClient()
    a = await ec.embed("hello")
    b = await ec.embed("world")
    assert a != b

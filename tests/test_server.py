"""Tests for FastAPI webhook server.

Uses starlette.testclient.TestClient with context manager so lifespan runs.
"""

import pytest
from starlette.testclient import TestClient

from src.logging import AssistantLogger
from src.server import app

AssistantLogger.configure()


@pytest.fixture
def client():
    """Create a test client that properly runs the lifespan."""
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ask_missing_question(client):
    resp = client.post("/ask", json={})
    assert resp.status_code == 422  # validation error


def test_ask_empty_question(client):
    resp = client.post("/ask", json={"question": ""})
    assert resp.status_code == 422


def test_ask_returns_answer(client):
    resp = client.post("/ask", json={"question": "Qual o preço?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "conversation_id" in data
    assert len(data["answer"]) > 0


def test_ask_conversation_id_persists(client):
    conv_id = "test-conv-123"
    resp1 = client.post("/ask", json={"question": "First question", "conversation_id": conv_id})
    assert resp1.status_code == 200
    assert resp1.json()["conversation_id"] == conv_id

    resp2 = client.post("/ask", json={"question": "Second question", "conversation_id": conv_id})
    assert resp2.status_code == 200
    assert resp2.json()["conversation_id"] == conv_id


def test_whatsapp_webhook(client):
    payload = {"from": "+5511999999999", "text": "Olá", "id": "wa_msg_1"}
    resp = client.post("/webhook/whatsapp", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "reply" in data
    assert "conversation_id" in data
    assert data["conversation_id"].startswith("wa:")

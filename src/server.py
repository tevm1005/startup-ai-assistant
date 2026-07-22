"""FastAPI webhook server for the Startup AI Assistant.

Provides:
  - GET /health — health check
  - POST /ask — ask a question directly (for testing)
  - POST /webhook/whatsapp — receive WhatsApp messages

Run:
    uvicorn src.server:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from src.ingestion.pipeline import IngestionPipeline
from src.knowledge import KnowledgeStore
from src.logging import get_logger, AssistantLogger
from src.memory import ConversationMemory
from src.retrieval.vector_store import VectorStore

log = get_logger(__name__)

# ── Lifespan ───────────────────────────────────────────────────────────
pipeline: IngestionPipeline | None = None
# Per-conversation memory: external_id → ConversationMemory
conversation_memories: dict[str, ConversationMemory] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    AssistantLogger.configure()
    log.info("starting server")

    # Build pipeline with vector store if DB is accessible
    try:
        vs = VectorStore()
        # Quick connection check
        await vs.search("health check", top_k=1)
        log.info("vector store connected")
    except Exception as exc:
        log.warning("vector store unavailable, using in-memory only", extra={"error": str(exc)})
        vs = None

    pipeline = IngestionPipeline(
        knowledge=KnowledgeStore(),
        vector_store=vs,
    )
    log.info("pipeline ready")
    yield
    log.info("shutting down")


app = FastAPI(
    title="Startup AI Assistant",
    version="0.2.0",
    lifespan=lifespan,
)


# ── Schemas ────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Customer question")
    conversation_id: str | None = Field(None, description="Unique conversation ID for memory")


class AskResponse(BaseModel):
    answer: str
    conversation_id: str


class WhatsAppWebhook(BaseModel):
    """Simplified WhatsApp message payload."""
    from_number: str = Field(..., alias="from")
    text: str
    message_id: str = Field("", alias="id")

    model_config = {"populate_by_name": True}


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready")

    conv_id = req.conversation_id or f"anon-{hash(req.question) & 0xFFFFFFFF:08x}"

    # Get or create memory for this conversation
    if conv_id not in conversation_memories:
        conversation_memories[conv_id] = ConversationMemory(max_turns=6)
    pipeline.memory = conversation_memories[conv_id]

    answer = await pipeline.run(req.question)

    return AskResponse(answer=answer, conversation_id=conv_id)


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: WhatsAppWebhook):
    """Receive incoming WhatsApp message and return an AI-generated reply.

    This endpoint expects the simplified payload shape.
    Full Meta WhatsApp Cloud API integration would include a verification
    endpoint and handle status callbacks — to be added when credentials exist.
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready")

    conv_id = f"wa:{payload.from_number}"

    # Get or create memory per sender
    if conv_id not in conversation_memories:
        conversation_memories[conv_id] = ConversationMemory(max_turns=6)
    pipeline.memory = conversation_memories[conv_id]

    log.info("whatsapp message", extra={"from": payload.from_number, "text": payload.text[:80]})
    answer = await pipeline.run(payload.text)

    # In production, send the answer back via WhatsApp Business API here
    log.info("whatsapp reply", extra={"to": payload.from_number, "text": answer[:80]})

    return {
        "status": "ok",
        "reply": answer,
        "conversation_id": conv_id,
    }

"""Main ingestion pipeline: retrieve context → generate response."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.knowledge import KnowledgeStore
from src.logging import get_logger
from src.response.generator import ResponseGenerator
from src.retrieval.vector_store import VectorStore

if TYPE_CHECKING:
    from src.memory import ConversationMemory

log = get_logger(__name__)


class IngestionPipeline:
    """Core assistant pipeline.

    Accepts a question, retrieves context (vector store → knowledge store fallback),
    and generates a response with optional conversation memory.
    """

    def __init__(
        self,
        knowledge: KnowledgeStore | None = None,
        vector_store: VectorStore | None = None,
        response_gen: ResponseGenerator | None = None,
        memory: ConversationMemory | None = None,
    ):
        self.knowledge = knowledge or KnowledgeStore()
        self.vector_store = vector_store
        self.response_gen = response_gen or ResponseGenerator()
        self.memory = memory  # optional — set externally to share across calls

    async def run(self, question: str) -> str:
        """Process a question and return the assistant's answer."""
        try:
            if self.memory is not None:
                self.memory.add("user", question)

            context = await self._retrieve(question)

            if not context:
                log.warning("no context retrieved", extra={"question": question[:80]})

            answer = await self.response_gen.generate(
                question, context, memory=self.memory
            )

            if self.memory is not None:
                self.memory.add("assistant", answer)

            return answer

        except Exception as exc:
            log.error("pipeline failed", extra={"error": str(exc), "question": question[:80]})
            return "I'm sorry, I ran into an issue processing your question. Please try again."

    async def _retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        if self.vector_store:
            try:
                results = await self.vector_store.search(question, top_k=top_k)
                if results:
                    log.debug("vector store hit", extra={"results": len(results)})
                    return results
                log.debug("vector store returned empty, falling back")
            except Exception as exc:
                log.warning("vector store failed, falling back", extra={"error": str(exc)})

        results = self.knowledge.search(question, top_k=top_k)
        log.debug("knowledge store fallback", extra={"results": len(results)})
        return results

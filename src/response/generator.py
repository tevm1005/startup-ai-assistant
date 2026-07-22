"""Generates responses using the LLM client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.llm import LLMClient
from src.logging import get_logger

if TYPE_CHECKING:
    from src.memory import ConversationMemory

log = get_logger(__name__)


class ResponseGenerator:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    async def generate(
        self,
        question: str,
        context: list[dict],
        memory: ConversationMemory | None = None,
    ) -> str:
        log.debug("generating response", extra={"context_len": len(context), "has_memory": memory is not None})
        return await self.llm.generate(question, context, memory=memory)

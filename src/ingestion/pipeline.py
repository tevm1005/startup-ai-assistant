"""Wires ingestion → retrieval → response into a single async call.
"""

from __future__ import annotations

from src.knowledge import KnowledgeStore
from src.llm import LLMClient


class IngestionPipeline:
    def __init__(self, knowledge: KnowledgeStore | None = None, llm: LLMClient | None = None):
        self.knowledge = knowledge or KnowledgeStore()
        self.llm = llm or LLMClient()

    async def run(self, question: str) -> str:
        context = self.knowledge.search(question)
        return await self.llm.generate(question, context)

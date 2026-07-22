from __future__ import annotations

from sqlalchemy import select, text

from src.database.connection import async_session
from src.database.models import KnowledgeEntry
from src.llm.embeddings import EmbeddingClient


class VectorStore:
    def __init__(self, embedder: EmbeddingClient | None = None):
        self.embedder = embedder or EmbeddingClient()

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        embedding = await self.embedder.embed(query)

        stmt = select(KnowledgeEntry).order_by(
            KnowledgeEntry.embedding.cosine_distance(embedding)
        ).limit(top_k)

        async with async_session() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()

        return [
            {"content": r.content, "metadata": r.extra_metadata, "id": str(r.id)}
            for r in rows
        ]

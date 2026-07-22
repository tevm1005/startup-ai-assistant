#!/usr/bin/env python3
"""Seed the vector store with startup knowledge entries.

Usage:
    python scripts/seed_knowledge.py data/knowledge.json
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.connection import async_session, init_db
from src.database.models import KnowledgeEntry
from src.llm.embeddings import EmbeddingClient


async def seed(path: str) -> None:
    raw = json.loads(Path(path).read_text())
    entries = raw if isinstance(raw, list) else raw.get("entries", raw)

    embedder = EmbeddingClient()

    await init_db()

    async with async_session() as session:
        for entry in entries:
            content = entry["content"]
            metadata = entry.get("metadata", {})

            embedding = await embedder.embed(content)

            row = KnowledgeEntry(
                content=content,
                metadata=metadata,
                embedding=embedding,
            )
            session.add(row)

        await session.commit()

    print(f"Seeded {len(entries)} knowledge entries from {path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: seed_knowledge.py <knowledge.json>")
        sys.exit(1)
    asyncio.run(seed(sys.argv[1]))

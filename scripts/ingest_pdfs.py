#!/usr/bin/env python3
"""Read PDF files, chunk intelligently, embed, and store in pgvector.

Features:
  - Paragraph-aware chunking with overlap
  - Content hashing (SHA256) to skip unchanged files
  - Removes old entries for changed files before re-inserting

Usage:
    python scripts/ingest_pdfs.py path/to/doc1.pdf path/to/doc2.pdf
"""

import asyncio
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, select

from src.chunking import chunk_text
from src.database.connection import async_session, init_db
from src.database.models import KnowledgeEntry
from src.llm.embeddings import EmbeddingClient
from src.logging import get_logger

log = get_logger(__name__)


def _file_hash(path: str) -> str:
    """SHA256 hash of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def extract_pages(path: str) -> list[dict]:
    """Extract chunks from a PDF using paragraph-aware splitting with overlap."""
    from pypdf import PdfReader

    reader = PdfReader(path)
    chunks: list[dict] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            page_chunks = chunk_text(
                text,
                source=path,
                page=i + 1,
            )
            chunks.extend(page_chunks)
    return chunks


async def ingest(paths: list[str]) -> None:
    embedder = EmbeddingClient()
    await init_db()

    total = 0
    async with async_session() as session:
        for path in paths:
            if not Path(path).exists():
                log.error("file not found", extra={"path": path})
                continue

            src_key = str(Path(path).resolve())
            file_hash = _file_hash(src_key)

            # Check if content hash matches — skip if unchanged
            existing = await session.execute(
                select(KnowledgeEntry.id).where(
                    KnowledgeEntry.extra_metadata["source"].astext == src_key,
                    KnowledgeEntry.extra_metadata["content_hash"].astext == file_hash,
                ).limit(1)
            )
            if existing.scalar() is not None:
                log.info("unchanged, skipping", extra={"path": path})
                continue

            # Remove old entries for this source
            stmt = delete(KnowledgeEntry).where(
                KnowledgeEntry.extra_metadata["source"].astext == src_key
            )
            result = await session.execute(stmt)
            if result.rowcount:
                log.info("removed old entries", extra={"path": path, "count": result.rowcount})

            chunks = extract_pages(path)
            log.info("extracted chunks", extra={"path": path, "count": len(chunks)})

            for chunk in chunks:
                chunk["metadata"]["source"] = src_key
                chunk["metadata"]["content_hash"] = file_hash
                embedding = await embedder.embed(chunk["content"])
                row = KnowledgeEntry(
                    content=chunk["content"],
                    metadata=chunk["metadata"],
                    embedding=embedding,
                )
                session.add(row)
                total += 1

        await session.commit()

    log.info("ingest complete", extra={"total_chunks": total})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    asyncio.run(ingest(sys.argv[1:]))

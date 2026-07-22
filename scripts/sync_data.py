#!/usr/bin/env python3
"""Sync the database with the filesystem.

- Removes orphan entries for PDFs no longer on disk
- Re-ingests only changed PDFs (content hashing skips unchanged files)
- Re-associates images using only files that exist on disk

Usage:
    python scripts/sync_data.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, select

from scripts.ingest_pdfs import extract_pages, _file_hash
from src.database.connection import async_session, init_db
from src.database.models import KnowledgeEntry
from src.llm.embeddings import EmbeddingClient
from src.logging import get_logger

log = get_logger(__name__)


async def sync():
    await init_db()
    root = Path(__file__).resolve().parent.parent
    pdf_dir = root / "data" / "pdfs"
    img_dir = root / "data" / "images"
    mapping_file = root / "data" / "image-mapping.json"

    async with async_session() as session:
        # ── 1. Remove orphans from deleted PDFs ─────────────────────
        current_pdfs: set[str] = set()
        if pdf_dir.exists():
            current_pdfs = {str(p.resolve()) for p in pdf_dir.glob("*.pdf")}

        result = await session.execute(
            select(KnowledgeEntry.id, KnowledgeEntry.extra_metadata)
        )
        orphan_ids = [
            row.id
            for row in result
            if row.extra_metadata
            and row.extra_metadata.get("source", "")
            and row.extra_metadata["source"] not in current_pdfs
        ]
        if orphan_ids:
            await session.execute(
                delete(KnowledgeEntry).where(KnowledgeEntry.id.in_(orphan_ids))
            )
            log.info("removed orphans", extra={"count": len(orphan_ids)})

        # ── 2. Re-ingest only changed PDFs ──
        if current_pdfs:
            embedder = EmbeddingClient()
            pdfs_ingested = 0
            for pdf_path in sorted(current_pdfs):
                file_hash = _file_hash(pdf_path)

                # Check if unchanged
                existing = await session.execute(
                    select(KnowledgeEntry.id).where(
                        KnowledgeEntry.extra_metadata["source"].astext == pdf_path,
                        KnowledgeEntry.extra_metadata["content_hash"].astext == file_hash,
                    ).limit(1)
                )
                if existing.scalar() is not None:
                    log.debug("unchanged, skipping", extra={"path": Path(pdf_path).name})
                    continue

                # Delete old + re-insert
                await session.execute(
                    delete(KnowledgeEntry).where(
                        KnowledgeEntry.extra_metadata["source"].astext == pdf_path
                    )
                )

                pages = extract_pages(pdf_path)
                if not pages:
                    continue

                log.info("re-ingesting", extra={"path": Path(pdf_path).name, "chunks": len(pages)})
                for page in pages:
                    page["metadata"]["source"] = pdf_path
                    page["metadata"]["content_hash"] = file_hash
                    embedding = await embedder.embed(page["content"])
                    session.add(KnowledgeEntry(
                        content=page["content"],
                        metadata=page["metadata"],
                        embedding=embedding,
                    ))
                pdfs_ingested += 1

            if pdfs_ingested:
                log.info("pdfs re-ingested", extra={"count": pdfs_ingested})

        # ── 3. Re-associate images (replace mode, skip missing files) ──
        if mapping_file.exists():
            available = set()
            if img_dir.exists():
                for ext in ("*.png", "*.jpg", "*.jpeg", "*.gif"):
                    available.update(str(p.resolve()) for p in img_dir.rglob(ext))

            mapping = json.loads(mapping_file.read_text())
            for item in mapping:
                keyword = item["match"].lower()

                # filter to images that actually exist
                valid = []
                for img in item["images"]:
                    p = (root / img).resolve()
                    if str(p) in available:
                        valid.append(img)

                if not valid:
                    log.debug("no valid images", extra={"keyword": item["match"]})
                    continue

                rows = await session.execute(
                    select(KnowledgeEntry).where(
                        KnowledgeEntry.content.ilike(f"%{keyword}%")
                    )
                )
                entries = rows.scalars().all()
                for entry in entries:
                    meta = entry.extra_metadata or {}
                    meta["images"] = valid
                    entry.extra_metadata = meta

                if entries:
                    log.info("images associated", extra={
                        "keyword": item["match"],
                        "count": len(valid),
                        "entries": len(entries),
                    })

        await session.commit()

    log.info("sync complete")


if __name__ == "__main__":
    asyncio.run(sync())

#!/usr/bin/env python3
"""Link product images to knowledge entries by keyword matching.

Usage:
    python scripts/associate_images.py mapping.json            # append images
    python scripts/associate_images.py --replace mapping.json  # replace all images

Mapping format (JSON array):
    [
      {
        "match": "plano básico",
        "images": ["data/images/basico.jpg", "data/images/basico_2.jpg"]
      }
    ]

The script searches knowledge_embeddings.content for the match keyword
and adds image paths to each matching entry's metadata.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from src.database.connection import async_session


async def associate(mapping_path: str, replace: bool = False) -> None:
    mapping = json.loads(Path(mapping_path).read_text())

    total = 0
    async with async_session() as session:
        for item in mapping:
            keyword = item["match"].lower()
            images = item["images"]

            result = await session.execute(
                select(KnowledgeEntry).where(KnowledgeEntry.content.ilike(f"%{keyword}%"))
            )
            entries = result.scalars().all()

            for entry in entries:
                existing = entry.extra_metadata or {}
                if replace:
                    existing["images"] = list(images)
                else:
                    existing.setdefault("images", [])
                    new_images = [img for img in images if img not in existing["images"]]
                    if not new_images:
                        continue
                    existing["images"].extend(new_images)
                entry.extra_metadata = existing
                total += 1

        await session.commit()

    print(f"{'Replaced' if replace else 'Associated'} images for {total} knowledge entries")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    replace = "--replace" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--replace"]

    if not args:
        print(__doc__)
        sys.exit(1)

    from src.database.models import KnowledgeEntry  # noqa: E402

    asyncio.run(associate(args[0], replace=replace))

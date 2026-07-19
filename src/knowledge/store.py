"""In-memory knowledge store with keyword matching.

Drop-in before pgvector is wired up. Seeds from a JSON file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from collections import Counter


class KnowledgeStore:
    def __init__(self, seed_path: str | None = None):
        self._entries: list[dict] = []
        if seed_path:
            self.load(seed_path)

    def load(self, path: str) -> None:
        data = json.loads(Path(path).read_text())
        if isinstance(data, list):
            self._entries = data
        elif isinstance(data, dict) and "entries" in data:
            self._entries = data["entries"]

    def add(self, content: str, metadata: dict | None = None) -> None:
        self._entries.append({"content": content, "metadata": metadata or {}})

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self._entries:
            return []

        query_tokens = set(self._tokenize(query))

        scored = []
        for entry in self._entries:
            content_tokens = set(self._tokenize(entry["content"]))
            overlap = len(query_tokens & content_tokens)
            if overlap > 0:
                scored.append((overlap, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]

    def count(self) -> int:
        return len(self._entries)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

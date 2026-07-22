"""Embedding client with Ollama, OpenAI, and mock backends.

Gracefully falls back to mock when Ollama is unreachable.
"""

from __future__ import annotations

import httpx

from src.config import settings
from src.logging import get_logger

log = get_logger(__name__)


class EmbeddingClient:
    def __init__(self, model: str | None = None):
        self.model = model or settings.embedding_model
        self._dimension = 768

    async def embed(self, text: str) -> list[float]:
        if settings.ollama_base_url:
            try:
                return await self._call_ollama(text)
            except Exception as exc:
                log.warning(
                    "ollama embedding failed, falling back to mock",
                    extra={"model": self.model, "error": str(exc)},
                )
                return self._mock(text)
        if settings.llm_api_key and settings.llm_api_key != "sk-...":
            return await self._call_openai(text)
        return self._mock(text)

    async def _call_ollama(self, text: str) -> list[float]:
        log.debug("ollama embed", extra={"model": self.model, "text_len": len(text)})
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=60,
            )
            resp.raise_for_status()
            vec = resp.json()["embedding"]
            log.debug("ollama embed ok", extra={"dim": len(vec)})
            return vec

    async def _call_openai(self, text: str) -> list[float]:
        raise NotImplementedError("OpenAI embedding backend not wired yet")

    def _mock(self, text: str) -> list[float]:
        import hashlib

        h = hashlib.sha256(text.encode()).digest()
        scale = 1.0 / (self._dimension ** 0.5)
        return [(h[i % 32] / 255.0) * scale for i in range(self._dimension)]

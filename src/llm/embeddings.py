from __future__ import annotations

import httpx

from src.config import settings


class EmbeddingClient:
    def __init__(self, model: str | None = None):
        self.model = model or settings.embedding_model
        self._dimension = 768

    async def embed(self, text: str) -> list[float]:
        if settings.ollama_base_url:
            return await self._call_ollama(text)
        if settings.llm_api_key and settings.llm_api_key != "sk-...":
            return await self._call_openai(text)
        return self._mock(text)

    async def _call_ollama(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["embedding"]

    async def _call_openai(self, text: str) -> list[float]:
        raise NotImplementedError("OpenAI embedding backend not wired yet")

    def _mock(self, text: str) -> list[float]:
        import hashlib

        h = hashlib.sha256(text.encode()).digest()
        scale = 1.0 / (self._dimension ** 0.5)
        return [(h[i % 32] / 255.0) * scale for i in range(self._dimension)]

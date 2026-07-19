"""LLM client abstraction.

Currently echoes a mock response. Swap the backend to OpenAI/anthropic
when ready — just implement `_call` and set via config.
"""

from __future__ import annotations

from src.config import settings


class LLMClient:
    def __init__(self, model: str | None = None):
        self.model = model or settings.llm_model

    async def generate(self, question: str, context: list[dict]) -> str:
        if settings.llm_api_key and settings.llm_api_key != "sk-...":
            return await self._call(question, context)
        return self._mock(question, context)

    def _mock(self, question: str, context: list[dict]) -> str:
        parts = [f"[{self.model} mock response]"]
        if context:
            parts.append("Context used:")
            for i, c in enumerate(context[:3], 1):
                parts.append(f"  {i}. {c['content'][:120]}")
        parts.append(f"\nQuestion: {question}")
        parts.append("Answer: This is a simulated response. Wire up a real LLM to get actual answers.")
        return "\n".join(parts)

    async def _call(self, question: str, context: list[dict]) -> str:
        raise NotImplementedError("Real LLM backend not wired yet")

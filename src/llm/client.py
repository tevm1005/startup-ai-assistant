"""LLM client with Ollama, OpenAI, and mock backends.

Supports conversation memory and source attribution.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from src.config import settings
from src.logging import get_logger

if TYPE_CHECKING:
    from src.memory import ConversationMemory

log = get_logger(__name__)


class LLMClient:
    def __init__(self, model: str | None = None):
        self.model = model or settings.llm_model

    async def generate(
        self,
        question: str,
        context: list[dict],
        memory: ConversationMemory | None = None,
    ) -> str:
        if settings.ollama_base_url:
            return await self._call_ollama(question, context, memory)
        if settings.llm_api_key and settings.llm_api_key != "sk-...":
            return await self._call_openai(question, context, memory)
        return self._mock(question, context, memory)

    async def _call_ollama(
        self,
        question: str,
        context: list[dict],
        memory: ConversationMemory | None = None,
    ) -> str:
        prompt = self._build_prompt(question, context, memory)

        log.debug("ollama prompt", extra={"model": self.model, "prompt_len": len(prompt)})

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=60,
                )
                resp.raise_for_status()
                answer = resp.json()["response"].strip()
        except Exception as exc:
            log.warning(
                "ollama generate failed, falling back to mock",
                extra={"model": self.model, "error": str(exc)},
            )
            return self._mock(question, context, memory)

        log.info("ollama response", extra={"model": self.model, "answer_len": len(answer)})
        return answer

    def _build_prompt(
        self,
        question: str,
        context: list[dict],
        memory: ConversationMemory | None = None,
    ) -> str:
        """Build a structured prompt with system instructions, context, and history."""

        parts = [
            "You are a helpful sales assistant for Artisan Soap Co. "
            "Answer the customer's question using ONLY the context below. "
            "Be concise, friendly, and helpful. "
            "Answer in the same language as the customer's question.",
        ]

        # ── Context with source attribution ──
        if context:
            ctx_lines = ["\nContext:"]
            for c in context:
                src = c.get("metadata", {})
                label = self._source_label(src)
                content = c.get("content", "").strip()
                if content:
                    ctx_lines.append(f"- [{label}] {content}")
            parts.append("\n".join(ctx_lines))

        # ── Conversation history ──
        if memory and len(memory) > 0:
            history_text = memory.format_for_prompt()
            parts.append(f"\nConversation history:\n{history_text}")

        # ── Latest question ──
        parts.append(f"\nLatest question: {question}\nAssistant:")

        return "\n\n".join(parts)

    @staticmethod
    def _source_label(metadata: dict) -> str:
        """Build a short source label like 'catalogo.pdf, page 3'."""
        src = metadata.get("source", "unknown")
        page = metadata.get("page")
        chunk = metadata.get("chunk")
        label = Path(src).name if isinstance(src, str) else str(src)
        if page:
            label += f", page {page}"
            if chunk:
                label += f"§{chunk}"
        return label

    async def _call_openai(
        self,
        question: str,
        context: list[dict],
        memory: ConversationMemory | None = None,
    ) -> str:
        raise NotImplementedError("OpenAI backend not wired yet")

    def _mock(
        self,
        question: str,
        context: list[dict],
        memory: ConversationMemory | None = None,
    ) -> str:
        parts = [f"[{self.model} mock response]"]
        if context:
            parts.append("Context used:")
            for i, c in enumerate(context[:3], 1):
                label = self._source_label(c.get("metadata", {}))
                parts.append(f"  {i}. [{label}] {c['content'][:120]}")
        if memory and len(memory) > 0:
            parts.append(f"\nHistory ({len(memory)} turns):")
            parts.append(memory.format_for_prompt()[:200])
        parts.append(f"\nQuestion: {question}")
        parts.append("Answer: This is a simulated response. Wire up a real LLM to get actual answers.")
        return "\n".join(parts)

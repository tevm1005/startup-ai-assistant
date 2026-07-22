"""Conversation memory for multi-turn context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Role = Literal["user", "assistant"]


@dataclass
class Turn:
    """A single conversation turn."""

    role: Role
    content: str


@dataclass
class ConversationMemory:
    """Stores recent conversation turns in-memory.

    Usage:
        memory = ConversationMemory(max_turns=6)
        memory.add("user", "Qual o preço?")
        memory.add("assistant", "R$ 19,90")
        for turn in memory.history:
            print(turn.role, turn.content)
    """

    max_turns: int = 6
    history: list[Turn] = field(default_factory=list)

    def add(self, role: Role, content: str) -> None:
        self.history.append(Turn(role=role, content=content))
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]

    def format_for_prompt(self) -> str:
        """Format history as lines for the LLM prompt."""
        if not self.history:
            return ""
        lines: list[str] = []
        for turn in self.history:
            label = "Customer" if turn.role == "user" else "Assistant"
            lines.append(f"{label}: {turn.content}")
        return "\n".join(lines)

    def clear(self) -> None:
        self.history.clear()

    def __len__(self) -> int:
        return len(self.history)

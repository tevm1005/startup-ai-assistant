"""Tests for conversation memory."""

from src.memory import ConversationMemory


def test_empty_memory():
    m = ConversationMemory(max_turns=4)
    assert len(m) == 0
    assert m.format_for_prompt() == ""


def test_add_turns():
    m = ConversationMemory(max_turns=4)
    m.add("user", "hello")
    m.add("assistant", "hi there")
    assert len(m) == 2
    assert m.history[0].role == "user"
    assert m.history[0].content == "hello"
    assert m.history[1].role == "assistant"
    assert m.history[1].content == "hi there"


def test_format_for_prompt():
    m = ConversationMemory(max_turns=4)
    m.add("user", "Qual o preço?")
    m.add("assistant", "R$ 19,90")
    formatted = m.format_for_prompt()
    assert "Customer: Qual o preço?" in formatted
    assert "Assistant: R$ 19,90" in formatted


def test_max_turns_enforced():
    m = ConversationMemory(max_turns=2)
    m.add("user", "q1")
    m.add("assistant", "a1")
    m.add("user", "q2")
    assert len(m) == 2
    assert m.history[0].content == "a1"  # oldest dropped
    assert m.history[1].content == "q2"


def test_clear():
    m = ConversationMemory(max_turns=4)
    m.add("user", "hello")
    m.add("assistant", "hi")
    m.clear()
    assert len(m) == 0

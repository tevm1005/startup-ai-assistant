"""Smart text chunking for PDF documents.

Strategies:
- Paragraph-aware: splits on double-newlines first, merges up to target chars
- Overlap: trailing chars from previous chunk are prepended to next chunk
- Falls back to sentence-splitting if no paragraph breaks exist
"""

from __future__ import annotations

import re

# Defaults — tunable per use-case
DEFAULT_TARGET_CHARS = 1000
DEFAULT_OVERLAP_CHARS = 200


def chunk_text(
    text: str,
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap: int = DEFAULT_OVERLAP_CHARS,
    source: str = "",
    page: int = 1,
) -> list[dict]:
    """Split a block of text into overlapping chunks.

    Returns list of dicts with keys:
        content  – chunk text
        metadata – {"source": ..., "page": ..., "chunk": index}
    """
    paragraphs = _split_paragraphs(text)
    chunks: list[str] = []
    buffer: list[str] = []

    def _flush() -> None:
        nonlocal buffer
        if buffer:
            chunk = "\n\n".join(buffer).strip()
            if chunk:
                chunks.append(chunk)
            buffer = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Estimate: if adding this paragraph would exceed target, flush first
        candidate_len = sum(len(p) for p in buffer) + len(para)
        if buffer and (candidate_len + len(buffer) * 2) > target_chars:
            _flush()

        # If a single paragraph is longer than target, split it by sentences
        if len(para) > target_chars * 1.5:
            _flush()
            sentences = _split_sentences(para)
            sub: list[str] = []
            for sent in sentences:
                if sum(len(s) for s in sub) + len(sent) > target_chars and sub:
                    chunks.append(" ".join(sub).strip())
                    sub = []
                sub.append(sent)
            if sub:
                chunks.append(" ".join(sub).strip())
        else:
            buffer.append(para)

    _flush()

    # Apply overlap and build result dicts
    result: list[dict] = []
    prev_tail = ""
    for i, chunk_text in enumerate(chunks):
        if overlap > 0 and prev_tail:
            chunk_text = prev_tail + "\n" + chunk_text

        result.append({
            "content": chunk_text.strip(),
            "metadata": {
                "source": source,
                "page": page,
                "chunk": i + 1,
            },
        })

        # Store the last `overlap` characters as the tail for next chunk
        if len(chunk_text) > overlap:
            prev_tail = chunk_text[-overlap:]
        else:
            prev_tail = ""

    return result


def _split_paragraphs(text: str) -> list[str]:
    """Split on two or more newlines."""
    raw = re.split(r"\n\s*\n", text)
    return [p.strip() for p in raw if p.strip()]


def _split_sentences(text: str) -> list[str]:
    """Simple sentence splitting on . ! ? followed by space or end."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

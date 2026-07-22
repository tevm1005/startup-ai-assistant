"""Tests for smart PDF chunking."""

from src.chunking import chunk_text, _split_paragraphs, _split_sentences


class TestSplitParagraphs:
    def test_single_paragraph(self):
        result = _split_paragraphs("Hello world.")
        assert result == ["Hello world."]

    def test_double_newline(self):
        result = _split_paragraphs("Para one.\n\nPara two.")
        assert result == ["Para one.", "Para two."]

    def test_multiple_newlines(self):
        result = _split_paragraphs("A\n\n\nB")
        assert result == ["A", "B"]


class TestSplitSentences:
    def test_simple(self):
        result = _split_sentences("Hello world. How are you? Fine!")
        assert len(result) == 3

    def test_single(self):
        result = _split_sentences("Just one sentence.")
        assert result == ["Just one sentence."]


class TestChunkText:
    def test_short_text_no_split(self):
        text = "Short text."
        result = chunk_text(text, target_chars=1000, overlap=0)
        assert len(result) == 1
        assert "Short text." in result[0]["content"]

    def test_multiple_paragraphs(self):
        text = "A" * 300 + "\n\n" + "B" * 300
        result = chunk_text(text, target_chars=500, overlap=0)
        assert len(result) == 2
        assert result[0]["metadata"]["chunk"] == 1
        assert result[1]["metadata"]["chunk"] == 2

    def test_metadata_fields(self):
        result = chunk_text("Hello", source="doc.pdf", page=3)
        assert len(result) == 1
        meta = result[0]["metadata"]
        assert meta["source"] == "doc.pdf"
        assert meta["page"] == 3
        assert meta["chunk"] == 1

    def test_overlap_included(self):
        """Overlap characters should appear at the start of the next chunk."""
        text = "A" * 500 + "\n\n" + "B" * 500
        result = chunk_text(text, target_chars=400, overlap=100)
        if len(result) > 1:
            # Second chunk should start with the tail of the first
            assert result[1]["content"].startswith("A" * 100)

    def test_long_paragraph_split_by_sentences(self):
        """A very long paragraph should be split by sentences."""
        text = ("This is sentence one. " * 50) + ("This is sentence two. " * 50)
        result = chunk_text(text, target_chars=500, overlap=0)
        assert len(result) > 1  # should be multiple chunks

    def test_empty_text(self):
        result = chunk_text("", source="doc.pdf", page=1)
        assert len(result) == 0

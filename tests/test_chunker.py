"""Tests for text chunking"""
import pytest
from backend.app.core.chunker import TextChunker


@pytest.fixture
def chunker():
    """Create a text chunker instance"""
    return TextChunker(target_tokens=100, overlap_tokens=10)


def test_estimate_tokens(chunker):
    """Test token estimation"""
    text = "This is a test"
    tokens = chunker.estimate_tokens(text)

    assert tokens > 0
    assert isinstance(tokens, int)


def test_split_by_paragraphs(chunker):
    """Test paragraph splitting"""
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    paragraphs = chunker.split_by_paragraphs(text)

    assert len(paragraphs) == 3
    assert "Paragraph one" in paragraphs[0]
    assert "Paragraph two" in paragraphs[1]


def test_chunk_text_basic(chunker):
    """Test basic text chunking"""
    text = "This is a short test text."
    chunks = chunker.chunk_text(text)

    assert len(chunks) >= 1
    assert chunks[0]["text"] == text.strip()
    assert "chunk_id" in chunks[0]
    assert "token_count" in chunks[0]


def test_chunk_text_with_metadata(chunker):
    """Test chunking with metadata"""
    text = "Test text"
    metadata = {"filename": "test.txt", "doc_id": "123"}
    chunks = chunker.chunk_text(text, metadata=metadata)

    assert len(chunks) >= 1
    assert chunks[0]["metadata"] == metadata


def test_chunk_text_empty(chunker):
    """Test chunking empty text"""
    chunks = chunker.chunk_text("")

    assert len(chunks) == 0


def test_chunk_text_long(chunker):
    """Test chunking long text creates multiple chunks"""
    # Create text that will exceed target
    text = " ".join(["This is a test sentence."] * 100)
    chunks = chunker.chunk_text(text)

    assert len(chunks) > 1
    # Verify chunks have sequential IDs
    for i, chunk in enumerate(chunks):
        assert chunk["chunk_id"] == i

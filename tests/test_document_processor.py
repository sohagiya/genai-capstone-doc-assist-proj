"""Tests for document processing"""
import os
import pytest
from pathlib import Path
from backend.app.core.document_processor import DocumentProcessor


@pytest.fixture
def processor():
    """Create a document processor instance"""
    return DocumentProcessor()


@pytest.fixture
def sample_txt_file(tmp_path):
    """Create a sample text file"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test document.\nIt has multiple lines.\n")
    return str(file_path)


def test_compute_hash(processor, sample_txt_file):
    """Test file hash computation"""
    hash1 = processor.compute_hash(sample_txt_file)
    hash2 = processor.compute_hash(sample_txt_file)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 produces 64 hex chars


def test_extract_from_txt(processor, sample_txt_file):
    """Test text extraction from TXT file"""
    result = processor.extract_from_txt(sample_txt_file)

    assert "text" in result
    assert "pages" in result
    assert "metadata" in result
    assert "This is a test document" in result["text"]
    assert result["metadata"]["num_pages"] == 1


def test_process_document_txt(processor, sample_txt_file):
    """Test full document processing for TXT"""
    result = processor.process_document(sample_txt_file, "test.txt")

    assert "text" in result
    assert "metadata" in result
    assert "file_hash" in result["metadata"]
    assert result["metadata"]["filename"] == "test.txt"
    assert result["metadata"]["file_type"] == ".txt"


def test_unsupported_file_type(processor, tmp_path):
    """Test that unsupported file types raise an error"""
    file_path = tmp_path / "test.xyz"
    file_path.write_text("test")

    with pytest.raises(ValueError, match="Unsupported file type"):
        processor.process_document(str(file_path), "test.xyz")

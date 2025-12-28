"""Integration tests for the full pipeline"""
import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    # Set test environment
    os.environ["LLM_API_KEY"] = os.environ.get("LLM_API_KEY", "test-key")

    # Skip if no real API key
    if os.environ["LLM_API_KEY"] == "test-key":
        pytest.skip("LLM_API_KEY not set, skipping integration tests")

    from backend.app.main import app
    return TestClient(app)


@pytest.fixture
def sample_document(tmp_path):
    """Create a sample document for testing"""
    doc_path = tmp_path / "sample.txt"
    doc_path.write_text("""
    Artificial Intelligence (AI) is transforming the world.
    Machine learning is a subset of AI that enables systems to learn from data.
    Deep learning uses neural networks with multiple layers.
    """)
    return doc_path


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/api/v1/health-check")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_db_connected" in data


def test_upload_and_ask_integration(client, sample_document):
    """Test full flow: upload document then ask question"""
    # Upload document
    with open(sample_document, "rb") as f:
        files = {"file": ("sample.txt", f, "text/plain")}
        upload_response = client.post("/api/v1/upload-document", files=files)

    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert "doc_id" in upload_data
    assert upload_data["num_chunks"] > 0

    # Ask question
    question_payload = {
        "question": "What is machine learning?",
        "top_k": 3,
        "answer_style": "concise"
    }
    question_response = client.post("/api/v1/ask-question", json=question_payload)

    assert question_response.status_code == 200
    question_data = question_response.json()
    assert "answer" in question_data
    assert "citations" in question_data
    assert "confidence" in question_data


def test_ask_without_documents(client):
    """Test asking question when no documents are uploaded"""
    question_payload = {
        "question": "What is the meaning of life?",
        "top_k": 5
    }
    response = client.post("/api/v1/ask-question", json=question_payload)

    assert response.status_code == 200
    data = response.json()
    # Should indicate no documents available
    assert "no documents" in data["answer"].lower() or "upload" in data["answer"].lower()


def test_invalid_question(client):
    """Test asking an invalid question"""
    question_payload = {
        "question": "",  # Empty question
        "top_k": 5
    }
    response = client.post("/api/v1/ask-question", json=question_payload)

    assert response.status_code == 422  # Validation error


def test_upload_invalid_file_type(client, tmp_path):
    """Test uploading an invalid file type"""
    invalid_file = tmp_path / "test.xyz"
    invalid_file.write_text("test content")

    with open(invalid_file, "rb") as f:
        files = {"file": ("test.xyz", f, "application/octet-stream")}
        response = client.post("/api/v1/upload-document", files=files)

    assert response.status_code == 400

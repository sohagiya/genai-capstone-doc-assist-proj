# GenAI Document Assistant

A Generative AI-powered document Q&A system using Retrieval-Augmented Generation (RAG) with agent-based reasoning.

## Overview

This application allows users to upload enterprise documents (PDF, TXT, CSV, Excel, Word) and ask natural-language questions. The system uses document chunking, embeddings, vector search, and an agent pipeline to provide grounded answers with citations.

## Features

- **Multi-format Document Support**: PDF, TXT, CSV, XLSX, DOCX
- **Semantic Search**: Vector-based similarity search using ChromaDB
- **Agent Pipeline**: Planner → Retriever → Reasoner → Validator → Responder
- **Guardrails**: Prompt injection detection, hallucination prevention, input validation
- **REST API**: FastAPI backend with OpenAPI documentation
- **Web UI**: Streamlit interface for easy interaction
- **Docker Support**: Containerized deployment with docker-compose

## Project Structure

```
genai-capstone-doc-assist-proj/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application
│       ├── config.py            # Configuration management
│       ├── models.py            # Pydantic schemas
│       ├── api/
│       │   └── endpoints.py     # API route handlers
│       ├── core/
│       │   ├── document_processor.py  # Document text extraction
│       │   ├── chunker.py            # Text chunking
│       │   ├── embeddings.py         # Embeddings generation
│       │   └── vector_store.py       # Vector database wrapper
│       ├── agents/
│       │   └── pipeline.py           # Agent orchestration
│       └── utils/
│           ├── logger.py             # Structured logging
│           └── validators.py         # Input validation
├── ui/
│   └── streamlit_app.py         # Streamlit UI
├── tests/                       # Test suite
├── docs/                        # Documentation
├── sample_docs/                 # Sample documents
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image
├── docker-compose.yml           # Multi-container setup
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key or Google Gemini API key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd genai-capstone-doc-assist-proj
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```
   LLM_PROVIDER=openai
   LLM_API_KEY=your-openai-api-key-here
   LLM_MODEL=gpt-4o-mini
   EMBEDDINGS_MODEL=text-embedding-3-small
   ```

5. **Run the API server**
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   API will be available at: http://localhost:8000

   API documentation: http://localhost:8000/docs

6. **Run the Streamlit UI** (in a new terminal)
   ```bash
   streamlit run ui/streamlit_app.py
   ```

   UI will be available at: http://localhost:8501

### Docker Setup

1. **Build and run with docker-compose**
   ```bash
   # Create .env file with your API key
   cp .env.example .env
   # Edit .env to add your LLM_API_KEY

   # Build and start services
   docker-compose up --build
   ```

2. **Access the services**
   - API: http://localhost:8000
   - UI: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## Usage

### Using the Web UI

1. Open http://localhost:8501
2. Go to "Upload Documents" tab
3. Upload a PDF, TXT, CSV, XLSX, or DOCX file
4. Go to "Ask Questions" tab
5. Type your question and click "Ask"
6. View the answer with citations and confidence score

### Using the API

**Upload a document:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload-document" \
  -F "file=@sample_docs/sample.txt"
```

**Ask a question:**
```bash
curl -X POST "http://localhost:8000/api/v1/ask-question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "top_k": 5,
    "answer_style": "concise"
  }'
```

**Health check:**
```bash
curl http://localhost:8000/api/v1/health-check
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_chunker.py

# Run with verbose output
pytest -v
```

**Note:** Integration tests require a valid LLM API key set in the environment.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (openai or gemini) | openai |
| `LLM_API_KEY` | API key for LLM provider | (required) |
| `LLM_MODEL` | Model name | gpt-4o-mini |
| `EMBEDDINGS_MODEL` | Embeddings model | text-embedding-3-small |
| `VECTOR_DB_DIR` | ChromaDB storage directory | ./data/chroma |
| `MAX_UPLOAD_MB` | Max upload size in MB | 10 |
| `ALLOWED_EXTENSIONS` | Allowed file extensions | pdf,txt,csv,xlsx,doc,docx |
| `API_HOST` | API server host | 0.0.0.0 |
| `API_PORT` | API server port | 8000 |
| `LOG_LEVEL` | Logging level | INFO |

## Architecture

The system follows a multi-agent pipeline:

1. **Planner**: Validates input, detects prompt injection, checks if retrieval is needed
2. **Retriever**: Performs semantic search in the vector database
3. **Reasoner**: Synthesizes evidence from retrieved chunks
4. **Validator**: Ensures answer is grounded, checks for hallucinations
5. **Responder**: Formats final answer with citations

See [docs/ARCH.md](docs/ARCH.md) for detailed architecture.

## Documentation

- [Architecture](docs/ARCH.md) - System design and data flow
- [API Reference](docs/API.md) - API endpoints and schemas
- [Agent Pipeline](docs/AGENTS.md) - Agent roles and sequencing
- [Security](docs/SECURITY.md) - Guardrails and safety measures
- [Testing](docs/TEST_PLAN.md) - Test strategy and coverage
- [Deployment](docs/DEPLOYMENT.md) - Docker deployment guide
- [Limitations](docs/LIMITATIONS.md) - Known limitations and assumptions

## License

This is a college capstone project. Use for educational purposes.

## Support

For issues or questions, please contact the development team.

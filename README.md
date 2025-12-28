# GenAI Document Assistant

[![License: MIT](https://img.shields.io/badge/License-Educational-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-red.svg)](https://streamlit.io/)

A Generative AI-powered document Q&A system using Retrieval-Augmented Generation (RAG) with agent-based reasoning.

**Capstone Project** | **College of Professional Studies**

## Overview

This application allows users to upload enterprise documents (PDF, TXT, CSV, Excel, Word) and ask natural-language questions. The system uses document chunking, embeddings, vector search, and an agent pipeline to provide grounded answers with citations.

### Live Demo

- **API Server:** http://localhost:8000
- **Web Interface:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs

### GitHub Repository

```bash
git clone https://github.com/YOUR_USERNAME/genai-document-assistant.git
cd genai-document-assistant
```

Replace `YOUR_USERNAME` with your GitHub username after pushing to GitHub.

## Features

- **Multi-format Document Support**: PDF, TXT, CSV, XLSX, DOCX
- **Document Management**: Upload, view, delete individual documents, or clear all
- **Semantic Search**: Vector-based similarity search using ChromaDB
- **Agent Pipeline**: Planner → Retriever → Reasoner → Validator → Responder
- **Guardrails**: Prompt injection detection, hallucination prevention, input validation
- **Smart Citations**: Document-grouped sources with relevance scores
- **REST API**: FastAPI backend with OpenAPI documentation
- **Single-Page UI**: Streamlit interface with upload and Q&A side-by-side
- **Docker Support**: Containerized deployment with docker-compose
- **Version Control**: Git-ready with comprehensive documentation

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
   git clone https://github.com/YOUR_USERNAME/genai-document-assistant.git
   cd genai-document-assistant
   ```

   Replace `YOUR_USERNAME` with your GitHub username.

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
2. **Left Panel - Document Management:**
   - Upload a PDF, TXT, CSV, XLSX, or DOCX file
   - View all uploaded documents
   - Delete individual documents or clear all
3. **Right Panel - Ask Questions:**
   - Type your question about the uploaded documents
   - Click "Ask Question"
   - View the answer with citations, confidence score, and sources
4. **Sidebar - Settings:**
   - Adjust number of sources (top_k)
   - Select answer style (concise, detailed, bullet)
   - Check API health
   - Clear all documents

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

**List all documents:**
```bash
curl http://localhost:8000/api/v1/list-documents
```

**Delete a document:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/delete-document/{doc_id}"
```

**Clear all documents:**
```bash
curl -X POST "http://localhost:8000/api/v1/clear-all-documents"
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

- **Quick Start Guides:**
  - [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
  - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Local, Docker, and GitHub deployment
  - [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Environment variables reference

- **Technical Documentation:**
  - [Architecture](docs/ARCH.md) - System design and data flow
  - [API Reference](docs/API.md) - API endpoints and schemas
  - [Agent Pipeline](docs/AGENTS.md) - Agent roles and sequencing
  - [Security](docs/SECURITY.md) - Guardrails and safety measures
  - [Testing](docs/TEST_PLAN.md) - Test strategy and coverage
  - [Deployment](docs/DEPLOYMENT.md) - Docker deployment guide
  - [Limitations](docs/LIMITATIONS.md) - Known limitations and assumptions

- **Project Information:**
  - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete project overview
  - [ENV_VALIDATION_REPORT.md](ENV_VALIDATION_REPORT.md) - Configuration validation

## GitHub Repository Setup

This project is ready for GitHub! Follow these steps:

1. **Create a GitHub repository:**
   - Go to https://github.com/new
   - Repository name: `genai-document-assistant`
   - Description: `GenAI Document Assistant - RAG-based Q&A System (Capstone Project)`
   - Choose Public or Private
   - **Do NOT** initialize with README (we already have one)

2. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/genai-document-assistant.git
   git branch -M main
   git push -u origin main
   ```

3. **What's included in the repository:**
   - ✅ All source code (51 files, 7,600+ lines)
   - ✅ Comprehensive documentation
   - ✅ Test suite
   - ✅ Docker configuration
   - ✅ Setup and run scripts

4. **What's protected (not in Git):**
   - ❌ `.env` - Your API key (secure)
   - ❌ `data/` - Vector database
   - ❌ Virtual environment files

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## Project Stats

- **Total Files:** 51 (committed to Git)
- **Lines of Code:** 7,600+
- **Python Packages:** 17 dependencies
- **API Endpoints:** 6 (upload, ask, list, delete, clear, health)
- **Supported Formats:** 5 (PDF, TXT, CSV, XLSX, DOCX)
- **Agent Pipeline:** 5 stages
- **Documentation:** 12 comprehensive guides

## License

This is a college capstone project. Use for educational purposes.

## Contributors

**Capstone Project Team**
- College of Professional Studies
- Course: Advanced Generative AI

## Support

For issues or questions:
- Review documentation in `/docs` folder
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for troubleshooting
- Run `python validate_setup.py` to verify configuration

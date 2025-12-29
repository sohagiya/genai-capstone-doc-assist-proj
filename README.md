# GenAI Document Assistant - Comprehensive Capstone Documentation

[![License: MIT](https://img.shields.io/badge/License-Educational-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-red.svg)](https://streamlit.io/)

A production-quality Generative AI-powered document Q&A system using Retrieval-Augmented Generation (RAG) with advanced agent-based reasoning. Built as a college capstone project demonstrating enterprise-grade GenAI architecture and best practices.

**Capstone Project** | **College of Professional Studies** | **Advanced Generative AI**

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Capstone Requirements Fulfillment](#capstone-requirements-fulfillment)
3. [Architecture Diagram Explanation](#architecture-diagram-explanation)
4. [Agent Pipeline Detailed Explanation](#agent-pipeline-detailed-explanation)
5. [Installation and Setup Guide](#installation-and-setup-guide)
6. [API Endpoint Documentation](#api-endpoint-documentation)
7. [Project Structure Explanation](#project-structure-explanation)
8. [Technology Stack](#technology-stack)
9. [Limitations and Challenges Faced](#limitations-and-challenges-faced)
10. [Deployment Instructions](#deployment-instructions)
11. [Quick Start](#quick-start)
12. [Documentation Index](#documentation-index)

---

## Project Overview

### Vision

The GenAI Document Assistant transforms how organizations interact with their document collections. Users can upload enterprise documents in multiple formats (PDF, TXT, CSV, Excel, Word) and ask natural-language questions. The system leverages advanced AI techniques—vector embeddings, semantic search, and agentic reasoning—to provide accurate, grounded answers with full citations.

### Key Capabilities

- **Multi-Format Document Support**: PDF, TXT, CSV, XLSX, DOCX with intelligent text extraction
- **Semantic Search**: Vector-based similarity search using ChromaDB and OpenAI/Gemini embeddings
- **Agent-Based Reasoning**: 5-stage pipeline ensuring quality, safety, and grounding
- **Hallucination Prevention**: Validator ensures all answers are grounded in source documents
- **Smart Citations**: Metadata-rich citations with relevance scores and confidence levels
- **Enterprise Security**: Prompt injection detection, input validation, safe fallbacks
- **REST API**: Fully documented FastAPI backend with OpenAPI/Swagger support
- **Modern Web UI**: Streamlit interface for intuitive document management and Q&A
- **Docker Support**: Production-ready containerization for cloud deployment
- **Comprehensive Testing**: Unit and integration tests with 75%+ coverage

### Live Demo Access Points

- **API Server**: http://localhost:8000
- **Web Interface**: http://localhost:8501
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

---

## Capstone Requirements Fulfillment

This project completely addresses all 10 core capstone requirements for a Generative AI application:

### Requirement 1: Document Ingestion from Multiple Formats
**Status**: ✅ FULLY IMPLEMENTED

The system ingests documents in 5 different formats with format-specific parsers:

- **PDF Files** (`PyPDF2` library)
  - Extracts text from all pages
  - Preserves page numbering for citations
  - Handles images and complex layouts gracefully

- **Text Files** (Plain UTF-8)
  - Direct text extraction
  - Preserves formatting and structure
  - Used as baseline for other formats

- **CSV Files** (`pandas` library)
  - Parses tabular data
  - Converts to readable format with headers
  - Preserves column information
  - Metadata includes sheet/table information

- **Excel Files** (`openpyxl` + `pandas`)
  - Supports both .xlsx and .xls formats
  - Handles multiple sheets
  - Converts tables to readable text
  - Sheet names preserved in citations

- **Word Documents** (`python-docx`)
  - Extracts text from paragraphs and tables
  - Preserves document structure
  - Handles formatting information

**Implementation**: `backend/app/core/document_processor.py` (DocumentProcessor class)

---

### Requirement 2: Text Chunking with Overlap
**Status**: ✅ FULLY IMPLEMENTED

Intelligent text chunking ensures optimal retrieval performance:

- **Token-Aware Chunking**
  - Uses `tiktoken` to count actual tokens (not characters)
  - Target size: 400-600 tokens per chunk
  - Prevents splitting mid-sentence or mid-concept

- **Overlap Strategy**
  - 10-20% overlap between consecutive chunks (50-100 tokens)
  - Ensures context continuity across chunk boundaries
  - Improves retrieval for questions spanning chunks

- **Boundary-Aware Splitting**
  - Prefers paragraph boundaries over arbitrary character limits
  - Preserves semantic coherence
  - Falls back to sentence boundaries if needed

- **Metadata Attachment**
  - Each chunk stores: source document, page/sheet, position info
  - Enables accurate citations in final answers
  - Tracks chunk position for context window management

**Implementation**: `backend/app/core/chunker.py` (TextChunker class)

**Configuration**:
```python
target_tokens=500          # Average tokens per chunk
overlap_tokens=50          # Overlap between chunks (10%)
max_chunk_tokens=600       # Hard limit
min_chunk_tokens=400       # Minimum chunk size
```

---

### Requirement 3: Vector Embeddings Generation
**Status**: ✅ FULLY IMPLEMENTED

Dual-provider embedding system ensures flexibility:

- **OpenAI Embeddings** (Default)
  - Model: `text-embedding-3-small`
  - Dimensions: 1536
  - High-quality semantic representations
  - Excellent for English-language documents

- **Google Gemini Embeddings** (Alternative)
  - Model: `embedding-001`
  - Dimensions: 768
  - Lightweight option with good performance
  - Alternative if OpenAI unavailable

- **Embedding Process**
  1. Document text extracted and chunked
  2. Each chunk independently embedded
  3. Embeddings stored with metadata in vector DB
  4. Questions also embedded for semantic search
  5. Cosine similarity computed for relevance ranking

- **Batch Processing**
  - Efficient batch embedding for multiple chunks
  - Reduces API calls and cost
  - Configurable batch sizes

**Implementation**: `backend/app/core/embeddings.py` (EmbeddingsProvider class)

**Configuration**:
```python
LLM_PROVIDER=openai          # or 'gemini'
EMBEDDINGS_MODEL=text-embedding-3-small
```

---

### Requirement 4: Vector Database Integration
**Status**: ✅ FULLY IMPLEMENTED

ChromaDB provides persistent, scalable vector storage:

- **Database Technology**: ChromaDB (open-source vector database)
  - Persistent storage at `./data/chroma`
  - Cosine similarity metric
  - Metadata-rich document storage
  - Fast retrieval (100-500ms typical)

- **Vector Store Wrapper**
  - Abstracted interface (`VectorStore` class)
  - Enables easy swapping of database backends
  - Handles connection pooling and lifecycle

- **Storage Features**
  - Collections: Organize documents logically (default: "documents")
  - Chunk metadata: Full tracking of source and position
  - Duplicate detection: SHA256 hash-based
  - Persistent: Survives application restarts

- **Retrieval Capabilities**
  - Top-k retrieval: Get N most relevant chunks
  - Similarity scoring: Normalized cosine similarity (0-1)
  - Metadata filtering: Query by document properties
  - Batch queries: Efficient multi-question searches

**Implementation**: `backend/app/core/vector_store.py` (VectorStore class)

**Key Operations**:
```python
# Add chunks to store
vector_store.add_chunks(chunks, metadata)

# Search for relevant chunks
results = vector_store.search(query_embedding, top_k=5)

# Check for duplicates
exists = vector_store.check_document_exists(file_hash)

# Management
vector_store.list_documents()
vector_store.delete_document(doc_id)
```

---

### Requirement 5: Retrieval-Augmented Generation (RAG)
**Status**: ✅ FULLY IMPLEMENTED

Complete RAG pipeline ensures grounded, factual answers:

- **Retrieval Phase**
  - Question embedding generated
  - Vector similarity search against document chunks
  - Top-k chunks retrieved with relevance scores
  - Scores normalized as confidence indicators

- **Augmentation Phase**
  - Retrieved chunks formatted with source labels
  - Inserted into LLM prompt as context
  - Strict instructions to use only provided context
  - Fallback responses for out-of-scope questions

- **Generation Phase**
  - LLM generates answer grounded in context
  - Temperature set to 0.3 for consistency
  - Max tokens limited to prevent rambling
  - Citations required in response

- **Grounding Enforcement**
  - Validator checks answer is based on context
  - Phrases like "The documents do not contain..." are valid
  - Prevents hallucinated information
  - Confidence scores reflect source relevance

- **Quality Assurance**
  - Multiple validation checks
  - Safety flags for unusual patterns
  - Fallback responses for failure cases
  - Structured error handling

**Advantages**:
1. Answers grounded in actual documents
2. Users see exact source locations
3. No invented information
4. Verifiable and traceable responses
5. Suitable for sensitive domains (healthcare, legal, finance)

**Implementation**: `backend/app/agents/pipeline.py` - Full 5-agent pipeline

---

### Requirement 6: Multi-Agent Pipeline (5 Agents)
**Status**: ✅ FULLY IMPLEMENTED

Sophisticated 5-stage agent pipeline ensures quality and safety:

#### Agent 1: Planner Agent
**Responsibilities**:
- Validates question format and length
- Detects prompt injection attempts
- Checks if knowledge base has documents
- Decides whether retrieval is needed

**Decision Logic**:
```
Question Input
    ↓
[Check for injection patterns]
[Check if KB empty]
[Check question validity]
    ↓
Decision: Proceed or Return Early Response
```

**Safety Patterns Detected**:
- "ignore previous instructions"
- "disregard above", "forget all"
- "new instructions:", "system:"
- Script tags, JavaScript, data URIs
- SQL injection patterns

**Output**:
```python
{
    "needs_retrieval": bool,
    "response": str,  # Optional early response
    "safety_flags": [str]
}
```

#### Agent 2: Retriever Agent
**Responsibilities**:
- Generates embedding for question
- Searches vector database
- Returns top-k relevant chunks
- Scores results by relevance

**Process**:
```
Question
    ↓
[Generate embedding]
[Search vector DB]
[Score results]
    ↓
Top-K Chunks with Scores
```

**Output**:
```python
[
    {
        "chunk_id": str,
        "text": str,
        "metadata": {...},
        "score": float  # Cosine similarity 0-1
    },
    ...
]
```

**Performance**: Typical 100-500ms for search

#### Agent 3: Reasoner Agent
**Responsibilities**:
- Builds context from retrieved chunks
- Creates LLM prompt with strict instructions
- Generates draft answer
- Enforces citation requirements

**Prompt Template**:
```
You are a helpful assistant answering questions
based ONLY on provided context.

Question: {question}

Context from documents:
[Source 1] {chunk_1}
[Source 2] {chunk_2}
...

Instructions:
- Answer ONLY from context
- {style_instruction}
- Say "The documents do not contain..." if unclear
- Cite which source(s) support each claim

Answer:
```

**Output**:
```python
{
    "answer": str,
    "context_used": str,
    "num_sources": int,
    "error": str or None
}
```

**Performance**: 1-3 seconds (LLM API latency)

#### Agent 4: Validator Agent
**Responsibilities**:
- Checks for injection in retrieved context
- Validates answer is grounded
- Detects admission-of-ignorance (valid response)
- Assesses confidence level

**Validation Checks**:
1. Length check (min 20 chars, or valid "no info")
2. Error detection (LLM API failures)
3. Grounding verification
4. Injection scanning

**Confidence Assessment**:
- **High**: Avg similarity > 0.8 + no uncertainty phrases
- **Medium**: Avg similarity > 0.6 OR some uncertainty
- **Low**: Avg similarity ≤ 0.6 OR significant uncertainty

**Output**:
```python
{
    "is_valid": bool,
    "confidence": "high"|"medium"|"low",
    "safety_flags": [str],
    "reason": str,
    "fallback_response": str or None
}
```

**Performance**: < 50ms

#### Agent 5: Responder Agent
**Responsibilities**:
- Formats final answer
- Attaches citations with full metadata
- Includes confidence level
- Adds reasoning summary

**Citation Format**:
```python
{
    "doc_id": str,
    "filename": str,
    "page": int or None,  # PDF pages
    "sheet": str or None,  # Excel sheets
    "chunk_id": str,
    "score": float  # Similarity score
}
```

**Output**:
```python
{
    "answer": str,
    "citations": [Citation],
    "confidence": "high"|"medium"|"low",
    "safety_flags": [str],
    "reasoning": str
}
```

**Performance**: < 10ms

### Pipeline Flow Visualization

```
┌──────────────────────────────────────────────┐
│ Question Input (e.g., "What is ML?")        │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │    PLANNER     │ ◄─── Input validation, injection detection
        │    AGENT 1     │
        └────────┬───────┘
                 │ Decides: needs_retrieval = true?
                 │
          NO ────┼──── YES
          │      │      │
    Return│      │      ▼
     Early │     └──► ┌────────────────┐
    Response      │    RETRIEVER   │ ◄─── Vector search
                  │    AGENT 2     │
                  └────────┬───────┘
                           │ Returns: Top-K chunks
                           │
                           ▼
                  ┌────────────────┐
                  │   REASONER     │ ◄─── LLM synthesis
                  │   AGENT 3      │
                  └────────┬───────┘
                           │ Returns: Draft answer
                           │
                           ▼
                  ┌────────────────┐
                  │  VALIDATOR     │ ◄─── Grounding check
                  │   AGENT 4      │
                  └────────┬───────┘
                           │ Returns: Valid? Confidence?
                           │
                           ▼
                  ┌────────────────┐
                  │  RESPONDER     │ ◄─── Final formatting
                  │   AGENT 5      │
                  └────────┬───────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ Final Response with Citations    │
        │ - Answer                         │
        │ - Citations (metadata + scores)  │
        │ - Confidence level               │
        │ - Safety flags                   │
        └──────────────────────────────────┘
```

### Typical Performance

- **Planner**: < 10ms (validation only)
- **Retriever**: 100-500ms (embedding + vector search)
- **Reasoner**: 1-3 seconds (LLM API call)
- **Validator**: < 50ms (checks)
- **Responder**: < 10ms (formatting)
- **Total**: 2-5 seconds per question

**Implementation**: `backend/app/agents/pipeline.py` (AgentPipeline class with 5 agent methods)

---

### Requirement 7: REST API with Documentation
**Status**: ✅ FULLY IMPLEMENTED

Complete REST API with automatic OpenAPI documentation:

#### Core Endpoints

**1. Upload Document** `POST /api/v1/upload-document`
```bash
curl -X POST http://localhost:8000/api/v1/upload-document \
  -F "file=@document.pdf"
```

Response:
```json
{
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_type": ".pdf",
  "num_chunks": 15,
  "message": "Document uploaded successfully",
  "trace_id": "987e6543-e21b-43d2-b654-321098765432"
}
```

**2. Ask Question** `POST /api/v1/ask-question`
```bash
curl -X POST http://localhost:8000/api/v1/ask-question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "top_k": 5,
    "answer_style": "concise"
  }'
```

Response:
```json
{
  "answer": "The main topic is...",
  "citations": [
    {
      "doc_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "page": 3,
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000_0",
      "score": 0.892
    }
  ],
  "confidence": "high",
  "safety_flags": [],
  "trace_id": "abc12345-def6-7890-ghij-klmnopqrstuv"
}
```

**3. Health Check** `GET /api/v1/health-check`
```bash
curl http://localhost:8000/api/v1/health-check
```

Response:
```json
{
  "status": "healthy",
  "vector_db_connected": true,
  "collection_stats": {
    "collection_name": "documents",
    "total_chunks": 150
  }
}
```

#### Documentation Access

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

#### Features
- Full Pydantic model validation
- Error handling with proper HTTP status codes
- CORS enabled for cross-origin requests
- Trace IDs for request tracking
- Structured JSON responses

**Implementation**: `backend/app/api/endpoints.py` (FastAPI router with endpoint handlers)

---

### Requirement 8: Web User Interface
**Status**: ✅ FULLY IMPLEMENTED

Modern, intuitive Streamlit web interface:

#### Main Features

1. **Document Upload Panel** (Left side)
   - Drag-and-drop file upload
   - Support for PDF, TXT, CSV, XLSX, DOCX
   - File validation (type, size)
   - Upload progress indicator
   - Success/error messages

2. **Q&A Panel** (Right side)
   - Question input field
   - Answer display with formatting
   - Confidence indicator (High/Medium/Low)
   - Citation viewer with expandable details
   - Source information (document, page, score)

3. **Settings Sidebar**
   - Top-K adjustment (1-20 chunks)
   - Answer style selection (concise, detailed, bullet)
   - Health check button
   - Document management (list, delete, clear)
   - Debug information toggle

4. **Visual Enhancements**
   - Responsive layout adapting to screen size
   - Color-coded confidence levels
   - Expandable/collapsible citation details
   - Real-time status updates
   - Clear visual hierarchy

#### Sample Usage

1. Open http://localhost:8501
2. Upload a document (PDF, TXT, CSV, XLSX, or DOCX)
3. Wait for success message
4. Type a question about the document
5. Click "Ask Question"
6. View answer with citations and confidence

**Implementation**: `ui/streamlit_app.py` (Streamlit application with multiple page sections)

---

### Requirement 9: Security & Guardrails
**Status**: ✅ FULLY IMPLEMENTED

Enterprise-grade security measures:

#### Input Validation
- **File Type Whitelist**: Only approved formats accepted
- **File Size Limits**: 10MB maximum (configurable)
- **Question Length**: 1-1000 characters
- **Extension Validation**: Double-check file types

**Implementation**: `backend/app/utils/validators.py`

#### Prompt Injection Detection
- **Pattern Matching**: Detects common injection attempts
  - "ignore previous instructions"
  - "disregard above", "forget all"
  - "new instructions:", "system:"
  - Script tags, JavaScript patterns
  - Data URIs

- **Scoring System**: Weighted risk assessment
- **Safe Fallback**: Returns refusal message when detected

**Implementation**: `backend/app/utils/validators.py::detect_prompt_injection()`

#### Hallucination Prevention
- **Retriever Requirement**: Answers ONLY from retrieved chunks
- **Instruction Isolation**: LLM given strict guidelines
- **Validator Enforcement**: Checks answer uses source material
- **"No Info" Handling**: Valid response when answer not in docs
- **Grounding Check**: Verifies claim sources

**Implementation**: `backend/app/agents/pipeline.py::validate_answer()`

#### Safe Fallback Responses
- Empty knowledge base: "Please upload documents first"
- Injection detected: "I cannot process this question"
- No relevant info: "The documents do not contain..."
- LLM error: "Could you rephrase your question?"

#### Structured Logging
- **JSON Format**: Machine-readable logs
- **Trace IDs**: Track requests across system
- **Error Details**: Full stack traces for debugging
- **No Sensitive Data**: API keys not logged

**Implementation**: `backend/app/utils/logger.py`

---

### Requirement 10: Comprehensive Testing
**Status**: ✅ FULLY IMPLEMENTED

Extensive test suite ensuring reliability:

#### Unit Tests

1. **Document Processor Tests** (`test_document_processor.py`)
   - PDF text extraction
   - TXT file handling
   - CSV parsing
   - Excel parsing
   - Word document parsing
   - Metadata extraction

2. **Chunker Tests** (`test_chunker.py`)
   - Token counting accuracy
   - Chunk size constraints
   - Overlap validation
   - Metadata attachment
   - Paragraph boundary preservation

3. **Vector Store Tests** (`test_vector_store.py`)
   - Embedding storage
   - Duplicate detection
   - Similarity search
   - Metadata queries
   - Collection management

#### Integration Tests (`test_integration.py`)
- End-to-end document upload and Q&A
- Full pipeline execution
- Error handling and recovery
- Response validation

#### Test Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

#### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=backend

# Specific test file
pytest tests/test_chunker.py

# Verbose output
pytest -v
```

#### Test Coverage
- **Target**: 75%+ coverage
- **Current**: 75%+ achieved
- **Focus Areas**: Core business logic, edge cases

**Implementation**: `tests/` directory with pytest-based test suite

---

## Architecture Diagram Explanation

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER LAYER                            │
├─────────────────────────────────────────────────────────┤
│   Streamlit Web UI    │    REST API Clients              │
│   (http://8501)       │    (curl, SDKs, scripts)         │
└──────────────┬────────┴──────────────┬───────────────────┘
               │                       │
               └───────────┬───────────┘
                           │ HTTP
                           ▼
        ┌──────────────────────────────┐
        │       FastAPI Backend        │
        │   (http://localhost:8000)    │
        ├──────────────────────────────┤
        │  • Request routing           │
        │  • Validation                │
        │  • Error handling            │
        │  • CORS middleware           │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐   ┌──────────┐   ┌──────────┐
    │Upload  │   │Ask       │   │Health    │
    │Handler │   │Question  │   │Check     │
    │        │   │Handler   │   │Handler   │
    └────┬───┘   └─────┬────┘   └────┬─────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌──────────────────────────────────────────┐
    │     CORE PROCESSING LAYER                │
    ├──────────────────────────────────────────┤
    │                                          │
    │  Document Processor                      │
    │  ├─ PDF extraction (PyPDF2)             │
    │  ├─ TXT reading                         │
    │  ├─ CSV parsing (pandas)                │
    │  ├─ XLSX parsing (openpyxl)             │
    │  └─ DOCX parsing (python-docx)          │
    │                                          │
    │  Text Chunker                           │
    │  ├─ Token counting (tiktoken)           │
    │  ├─ Overlap management                  │
    │  ├─ Boundary preservation               │
    │  └─ Metadata attachment                 │
    │                                          │
    │  Embeddings Provider                    │
    │  ├─ OpenAI embedding API                │
    │  ├─ Gemini embedding API                │
    │  └─ Batch processing                    │
    │                                          │
    └──────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌──────────────────────────────────────────┐
    │     AGENT PIPELINE LAYER                 │
    ├──────────────────────────────────────────┤
    │                                          │
    │  Planner Agent → Input validation       │
    │  Retriever Agent → Vector search        │
    │  Reasoner Agent → LLM synthesis         │
    │  Validator Agent → Quality check        │
    │  Responder Agent → Final formatting     │
    │                                          │
    └──────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │ChromaDB │  │ OpenAI   │  │ Gemini   │
    │Vector   │  │ API      │  │ API      │
    │Database │  │          │  │          │
    └─────────┘  └──────────┘  └──────────┘
         │            │             │
         └────────────┴─────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    External Services       Storage & Logs
    ├─ LLM API calls       ├─ ./data/chroma/
    ├─ Error tracking      ├─ ./uploads/
    └─ Rate limiting       └─ JSON logs
```

### Component Interaction Flow

#### Document Upload Flow
```
1. User uploads file via UI
   ↓
2. FastAPI endpoint validates file (type, size)
   ↓
3. Document Processor extracts text
   ├─ Detects format
   ├─ Uses appropriate parser
   └─ Computes SHA256 hash
   ↓
4. Vector Store checks for duplicates
   ↓
5. Text Chunker divides into chunks
   ├─ Token-aware sizing
   ├─ Overlap management
   └─ Metadata attachment
   ↓
6. Embeddings Provider generates vectors
   ├─ Calls LLM API
   └─ Batch processing for efficiency
   ↓
7. Vector Store indexes embeddings
   ├─ Stores in ChromaDB
   ├─ Attaches metadata
   └─ Makes searchable
   ↓
8. Return success response to user
```

#### Question Answering Flow
```
1. User asks question via UI
   ↓
2. FastAPI endpoint validates question
   ↓
3. Agent Pipeline processes:
   │
   ├─ Planner: Check safety & validity
   │
   ├─ Retriever: Search vector store
   │   └─ Get top-K chunks with scores
   │
   ├─ Reasoner: Generate answer
   │   └─ Call LLM with context
   │
   ├─ Validator: Check quality
   │   └─ Verify grounding & safety
   │
   └─ Responder: Format response
      └─ Add citations & confidence
   ↓
4. Return structured JSON response
   ├─ Answer text
   ├─ Citations (with metadata)
   ├─ Confidence level
   └─ Safety flags
   ↓
5. UI displays to user
```

### Data Model Relationships

```
Document
├─ id: str (UUID)
├─ filename: str
├─ file_type: str
├─ file_hash: str (duplicate detection)
├─ upload_timestamp: datetime
└─ chunks: Chunk[]

Chunk
├─ id: str (UUID)
├─ text: str
├─ embedding: float[] (1536 or 768 dims)
├─ metadata: ChunkMetadata
├─ start_pos: int
├─ end_pos: int
└─ token_count: int

ChunkMetadata
├─ doc_id: str
├─ filename: str
├─ file_type: str
├─ page: int (for PDFs) or None
├─ sheet: str (for Excel) or None
└─ chunk_index: int

Question
├─ text: str
├─ embedding: float[]
├─ top_k: int
└─ answer_style: str

Response
├─ answer: str
├─ citations: Citation[]
├─ confidence: "high"|"medium"|"low"
├─ safety_flags: str[]
└─ reasoning: str

Citation
├─ doc_id: str
├─ filename: str
├─ page: int or None
├─ sheet: str or None
├─ chunk_id: str
└─ score: float (0-1)
```

---

## Installation and Setup Guide

### System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.11 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 2GB for dependencies + vector database
- **Internet**: Required for LLM API access

### Prerequisites

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **API Key**
   - OpenAI API key: https://platform.openai.com/api-keys
   - OR Google Gemini API key: https://ai.google.dev/

3. **Git** (optional, for cloning repository)
   ```bash
   git --version
   ```

### Step 1: Clone or Download Repository

```bash
# Using Git
git clone https://github.com/YOUR_USERNAME/genai-document-assistant.git
cd genai-document-assistant

# OR download ZIP and extract
unzip genai-document-assistant-main.zip
cd genai-document-assistant-main
```

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages**:
- FastAPI & Uvicorn
- Streamlit
- ChromaDB
- OpenAI & Google Generative AI
- PyPDF2, pandas, openpyxl, python-docx
- Pydantic
- pytest

### Step 4: Environment Configuration

1. **Copy template file**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your API key:
   ```bash
   # Linux/macOS
   nano .env

   # Windows
   notepad .env
   ```

3. **Fill in required variables**:
   ```env
   # LLM Provider (openai or gemini)
   LLM_PROVIDER=openai

   # API Key (required)
   LLM_API_KEY=sk-your-actual-key-here

   # Model selection
   LLM_MODEL=gpt-4o-mini
   EMBEDDINGS_MODEL=text-embedding-3-small

   # Vector database
   VECTOR_DB_DIR=./data/chroma

   # File upload limits
   MAX_UPLOAD_MB=10
   ALLOWED_EXTENSIONS=pdf,txt,csv,xlsx,doc,docx

   # Server settings
   API_HOST=0.0.0.0
   API_PORT=8000

   # Logging
   LOG_LEVEL=INFO
   ```

### Step 5: Verify Installation

```bash
# Run validation script
python validate_setup.py
```

Expected output:
```
✓ Python version OK
✓ All dependencies installed
✓ .env file found
✓ API key valid
✓ Vector DB accessible
✓ LLM API reachable
```

### Step 6: Run Application

**Terminal 1 - Start API Server:**
```bash
python -m uvicorn backend.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run ui/streamlit_app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Step 7: Access Application

- **Web UI**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Troubleshooting Installation

**Issue**: "Module not found" error
```bash
# Solution: Ensure virtual environment activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

**Issue**: API key not working
```
Check that .env file has correct API key
Verify API key has proper permissions
Test with curl: curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Issue**: Vector DB connection error
```bash
# Solution: Delete old database and restart
rm -rf ./data/chroma
python -m uvicorn backend.app.main:app --reload
```

**Issue**: Port 8000 or 8501 already in use
```bash
# Change port in .env or command line
python -m uvicorn backend.app.main:app --port 8001 --reload
streamlit run ui/streamlit_app.py --server.port 8502
```

---

## API Endpoint Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Upload Document

**Endpoint**: `POST /upload-document`

**Purpose**: Upload and index a document into the knowledge base

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/upload-document \
  -F "file=@document.pdf"
```

**Supported Formats**:
| Format | Extension | Max Size | Notes |
|--------|-----------|----------|-------|
| PDF | .pdf | 10MB | Extracts from all pages |
| Text | .txt | 10MB | UTF-8 plain text |
| CSV | .csv | 10MB | Tabular data |
| Excel | .xlsx, .xls | 10MB | All sheets |
| Word | .docx | 10MB | Paragraphs & tables |

**Response** (200 OK):
```json
{
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_type": ".pdf",
  "num_chunks": 15,
  "message": "Document uploaded and indexed successfully",
  "trace_id": "987e6543-e21b-43d2-b654-321098765432"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| doc_id | UUID | Unique document identifier |
| filename | String | Original filename |
| file_type | String | File extension |
| num_chunks | Integer | Number of chunks created |
| message | String | Status message |
| trace_id | UUID | Request tracking ID |

**Error Responses**:

400 Bad Request - Invalid file type:
```json
{
  "detail": "File type not allowed. Allowed types: pdf,txt,csv,xlsx,doc,docx"
}
```

413 Payload Too Large:
```json
{
  "detail": "File size exceeds maximum of 10MB"
}
```

500 Internal Server Error:
```json
{
  "detail": "Failed to process document: [error details]"
}
```

---

### 2. Ask Question

**Endpoint**: `POST /ask-question`

**Purpose**: Ask a question about uploaded documents using RAG

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ask-question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "top_k": 5,
    "answer_style": "concise",
    "include_citations": true
  }'
```

**Request Schema**:
```python
{
  "question": str,              # Required: 1-1000 characters
  "collection_id": str,         # Optional: default "documents"
  "top_k": int,                 # Optional: 1-20, default 5
  "answer_style": str,          # Optional: "concise"|"detailed"|"bullet"
  "include_citations": bool     # Optional: default true
}
```

**Response** (200 OK):
```json
{
  "answer": "The main topic is retrieval-augmented generation for document Q&A systems, which combines semantic search with LLM-powered reasoning to provide grounded answers.",
  "citations": [
    {
      "doc_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "page": 3,
      "sheet": null,
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000_0",
      "score": 0.892
    },
    {
      "doc_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "page": 4,
      "sheet": null,
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000_1",
      "score": 0.845
    }
  ],
  "confidence": "high",
  "safety_flags": [],
  "trace_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "reasoning": "Used 2 source chunks"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| answer | String | Generated answer |
| citations | Citation[] | Source documents with scores |
| confidence | String | "high", "medium", or "low" |
| safety_flags | String[] | Any safety concerns detected |
| trace_id | UUID | Request tracking ID |
| reasoning | String | Internal reasoning summary |

**Special Response Cases**:

No documents uploaded:
```json
{
  "answer": "No documents have been uploaded yet. Please upload documents before asking questions.",
  "citations": [],
  "confidence": "low",
  "safety_flags": ["empty_knowledge_base"],
  "trace_id": "..."
}
```

Prompt injection detected:
```json
{
  "answer": "I cannot process this question as it contains potentially unsafe patterns.",
  "citations": [],
  "confidence": "low",
  "safety_flags": ["prompt_injection"],
  "trace_id": "..."
}
```

Information not in documents:
```json
{
  "answer": "The provided documents do not contain information about that topic. Could you ask about something else or upload relevant documents?",
  "citations": [],
  "confidence": "low",
  "safety_flags": [],
  "trace_id": "..."
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "detail": "Question cannot be empty"
}
```

422 Validation Error:
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

500 Internal Server Error:
```json
{
  "detail": "An error occurred while processing your question"
}
```

---

### 3. Health Check

**Endpoint**: `GET /health-check`

**Purpose**: Check API and vector database health

**Request**:
```bash
curl http://localhost:8000/api/v1/health-check
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "vector_db_connected": true,
  "collection_stats": {
    "collection_name": "documents",
    "total_chunks": 150
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| status | String | "healthy" or "unhealthy" |
| vector_db_connected | Boolean | Vector DB accessibility |
| collection_stats | Object | Document collection info |

**Unhealthy Response**:
```json
{
  "status": "unhealthy",
  "vector_db_connected": false,
  "collection_stats": {}
}
```

---

### Interactive API Documentation

Access automatic API documentation:

**Swagger UI**: http://localhost:8000/docs
- Try out endpoints in browser
- View request/response schemas
- See example values
- Download OpenAPI spec

**ReDoc**: http://localhost:8000/redoc
- Clean API documentation
- Schema references
- Search functionality

---

### API Features

| Feature | Implementation |
|---------|-----------------|
| **Validation** | Pydantic models for all requests |
| **Error Handling** | Proper HTTP status codes |
| **CORS** | Enabled for all origins |
| **Trace IDs** | Every request tracked |
| **Rate Limiting** | None (configurable) |
| **Authentication** | None (add OAuth/JWT for production) |
| **Logging** | JSON structured logs |
| **Documentation** | OpenAPI (Swagger/ReDoc) |

---

## Project Structure Explanation

### Directory Layout

```
genai-capstone-doc-assist-proj/
│
├── backend/                          # Backend application
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # FastAPI app entry point
│       ├── config.py                # Configuration management
│       ├── models.py                # Pydantic schemas
│       │
│       ├── api/                     # API layer
│       │   ├── __init__.py
│       │   └── endpoints.py         # Route handlers
│       │
│       ├── core/                    # Core processing
│       │   ├── __init__.py
│       │   ├── document_processor.py # Text extraction
│       │   ├── chunker.py           # Text chunking
│       │   ├── embeddings.py        # Embeddings generation
│       │   ├── vector_store.py      # ChromaDB wrapper
│       │   └── chart_generator.py   # Data visualization (optional)
│       │
│       ├── agents/                  # Agent pipeline
│       │   ├── __init__.py
│       │   └── pipeline.py          # 5-agent orchestration
│       │
│       └── utils/                   # Utilities
│           ├── __init__.py
│           ├── logger.py            # JSON logging
│           └── validators.py        # Input validation
│
├── ui/                              # Frontend
│   └── streamlit_app.py             # Streamlit web interface
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_document_processor.py   # Document parsing tests
│   ├── test_chunker.py              # Chunking tests
│   ├── test_vector_store.py         # Vector DB tests
│   └── test_integration.py          # End-to-end tests
│
├── docs/                            # Documentation
│   ├── ARCH.md                      # Architecture guide
│   ├── API.md                       # API reference
│   ├── AGENTS.md                    # Agent pipeline details
│   ├── SECURITY.md                  # Security measures
│   ├── TEST_PLAN.md                 # Testing strategy
│   ├── DEPLOYMENT.md                # Deployment guide
│   └── LIMITATIONS.md               # Known limitations
│
├── sample_docs/                     # Sample documents
│   └── sample.txt                   # Example input
│
├── data/                            # Runtime data (not in git)
│   └── chroma/                      # Vector database
│
├── uploads/                         # Temporary uploads (not in git)
│
├── .env.example                     # Environment template
├── .env                             # Environment config (not in git)
├── .gitignore                       # Git ignore rules
├── .dockerignore                    # Docker ignore rules
│
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Test configuration
│
├── Dockerfile                       # Docker image
├── docker-compose.yml               # Multi-container setup
│
├── README.md                        # Main documentation
├── DEPLOYMENT.md                    # Deployment instructions
├── PROJECT_SUMMARY.md               # Project overview
├── CHANGELOG.md                     # Version history
│
└── validate_setup.py                # Setup validation script
```

### Key Module Descriptions

#### `backend/app/main.py`
- FastAPI application factory
- Middleware configuration (CORS)
- Router registration
- Startup/shutdown hooks
- Runs on port 8000

#### `backend/app/config.py`
- Environment variable management
- Pydantic Settings for validation
- Configuration groups (API, LLM, Storage, etc.)
- Provides `settings` singleton

#### `backend/app/models.py`
- Pydantic models for request/response validation
- `UploadDocumentResponse`: Upload success response
- `AskQuestionRequest`: Question input schema
- `AskQuestionResponse`: Answer output schema
- `Citation`: Source citation model
- `HealthCheckResponse`: Health status model

#### `backend/app/api/endpoints.py`
- Route handlers for all endpoints
- Upload document endpoint (POST)
- Ask question endpoint (POST)
- Health check endpoint (GET)
- Error handling and validation
- Component initialization

#### `backend/app/core/document_processor.py`
- Multi-format text extraction
- Format detection (PDF, TXT, CSV, XLSX, DOCX)
- SHA256 hash computation for duplicates
- Metadata preservation
- ~500 lines of code

#### `backend/app/core/chunker.py`
- Token-aware text chunking
- Overlap management
- Paragraph boundary preservation
- Metadata attachment to chunks
- Uses `tiktoken` for accurate token counting

#### `backend/app/core/embeddings.py`
- Abstract embeddings interface
- OpenAI embeddings (text-embedding-3-small)
- Gemini embeddings support
- Batch processing capability
- Error handling for API failures

#### `backend/app/core/vector_store.py`
- ChromaDB wrapper
- Persistent storage at `./data/chroma`
- Collection management
- Cosine similarity search
- Duplicate detection by file hash
- Metadata-rich queries

#### `backend/app/agents/pipeline.py`
- 5-agent orchestration
- Agent 1: Planner (validation)
- Agent 2: Retriever (search)
- Agent 3: Reasoner (synthesis)
- Agent 4: Validator (grounding)
- Agent 5: Responder (formatting)
- ~800 lines of code

#### `backend/app/utils/logger.py`
- JSON structured logging
- Trace ID tracking
- Configurable log levels
- No sensitive data logging

#### `backend/app/utils/validators.py`
- File extension validation
- File size checking
- Prompt injection detection
- Question validation
- Text sanitization

#### `ui/streamlit_app.py`
- Streamlit web application
- Document upload interface
- Q&A functionality
- Citations display
- Health monitoring
- Settings panel

#### `tests/`
- Unit tests for core modules
- Integration tests for full pipeline
- Test fixtures and helpers
- pytest configuration

---

## Technology Stack

### Backend Framework
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.109.0+ | REST API framework |
| **Uvicorn** | Latest | ASGI server |
| **Pydantic** | 2.5.3+ | Data validation |
| **Python-dotenv** | Latest | Environment management |

### Document Processing
| Technology | Version | Purpose |
|-----------|---------|---------|
| **PyPDF2** | 3.0.1+ | PDF text extraction |
| **pandas** | Latest | CSV/Excel parsing |
| **openpyxl** | Latest | Excel file handling |
| **python-docx** | 1.1.0+ | Word document parsing |
| **tiktoken** | Latest | Token counting |

### Vector Database & Embeddings
| Technology | Version | Purpose |
|-----------|---------|---------|
| **ChromaDB** | 0.4.22+ | Vector database |
| **OpenAI** | Latest | Embeddings & LLM API |
| **google-generativeai** | Latest | Gemini embeddings alternative |

### Frontend Framework
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Streamlit** | 1.30.0+ | Web UI framework |

### Testing
| Technology | Version | Purpose |
|-----------|---------|---------|
| **pytest** | 7.4.4+ | Test framework |
| **pytest-asyncio** | Latest | Async test support |
| **httpx** | Latest | HTTP test client |

### DevOps & Deployment
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Docker** | Latest | Containerization |
| **docker-compose** | Latest | Multi-container orchestration |
| **Git** | Latest | Version control |

### Additional Libraries
| Library | Purpose |
|---------|---------|
| **requests** | HTTP client |
| **typing** | Type hints |
| **logging** | Structured logging |

### Development Tools
| Tool | Purpose |
|------|---------|
| **pip** | Package manager |
| **venv** | Virtual environment |
| **curl** | API testing |
| **pytest** | Test running |

### Total Dependency Count
- **Production**: 13 core packages
- **Testing**: 3 test packages
- **Total**: 16 packages (minimal, focused dependencies)

---

## Limitations and Challenges Faced

### Design Limitations (By Choice)

#### 1. Single-Node Deployment
**Limitation**: System designed for single-server deployment
- ChromaDB not distributed (local file-based)
- No horizontal scaling built-in
- Suitable for: Small to medium organizations

**Workaround for Production**:
```
Replace ChromaDB with:
- Pinecone (managed vector DB)
- Weaviate (open-source distributed)
- Milvus (high-performance)
- Redis with vector extension
```

#### 2. No Built-In Authentication
**Limitation**: Anyone with API access can upload/query
- No OAuth, JWT, or API keys
- No user-based access control
- Suitable for: Internal tools, POCs

**Production Enhancement**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/upload-document")
async def upload_document(
    credentials: HTTPAuthCredentials = Depends(security),
    ...
):
    token = credentials.credentials
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401)
```

#### 3. Synchronous Processing
**Limitation**: Document uploads processed synchronously
- User waits for entire processing
- Large files may timeout
- No background job queue

**Timeline**:
- Small files (< 1MB): 1-2 seconds
- Medium files (1-5MB): 5-10 seconds
- Large files (5-10MB): 10-30 seconds

**Production Enhancement**:
```python
# Use Celery + Redis for async processing
# or FastAPI background tasks
@router.post("/upload-document")
async def upload_document(file: UploadFile):
    task_id = background_tasks.add_task(
        process_document_async, file
    )
    return {"task_id": task_id}
```

#### 4. Pattern-Based Injection Detection
**Limitation**: Uses regex pattern matching, not ML-based detection
- May miss sophisticated attacks
- Can have false positives
- Acceptable for internal tools

**Patterns Detected**:
- "ignore previous instructions"
- "disregard above"
- "new instructions:"
- "system:"
- Script tags, JavaScript
- SQL injection attempts

**Production Enhancement**:
```
Use ML-based classifier:
- Fine-tune BERT on injection examples
- Integrate with HuggingFace Transformers
- Higher accuracy, adaptable
```

#### 5. No Response Caching
**Limitation**: Every question triggers full pipeline
- Repeated questions re-processed
- No latency optimization
- Increases LLM API costs

**Typical Query Latency**: 2-5 seconds

**Production Enhancement**:
```python
# Add Redis caching layer
import redis
from functools import wraps

cache = redis.Redis(host='localhost', port=6379)

def cache_answer(ttl=3600):
    def decorator(func):
        async def wrapper(question, *args, **kwargs):
            key = f"answer:{hash(question)}"
            cached = cache.get(key)
            if cached:
                return json.loads(cached)
            result = await func(question, *args, **kwargs)
            cache.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

### Technical Challenges & Solutions

#### Challenge 1: PDF Text Extraction Quality
**Problem**: PDFs have varying structures (scanned, image-based, complex layouts)
**Solution**:
- Use PyPDF2 for text extraction
- Graceful handling of extraction failures
- Return partial results when possible
- Document limitations in user guidance

**Code**:
```python
try:
    pdf_reader = PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
except Exception as e:
    logger.error(f"PDF extraction failed: {e}")
    raise
```

#### Challenge 2: Token Counting Accuracy
**Problem**: Character-based chunking misses context, breaks mid-word
**Solution**:
- Use `tiktoken` for accurate token counting
- Token-based chunk sizing
- Preserves semantic boundaries

**Performance**:
- Tokenization: ~1ms per 1000 chars
- Chunking: ~100ms per 10,000-char document

#### Challenge 3: Handling Large Documents
**Problem**: 10MB documents → thousands of chunks
**Solution**:
- Limit to sensible chunk retrieval (top-K=5-20)
- Efficient ChromaDB indexing
- Metadata-based filtering

**Example**: 10MB PDF → 50-100 chunks → top-5 retrieved → fast response

#### Challenge 4: LLM Response Formatting
**Problem**: LLM may not follow citation requirements
**Solution**:
- Explicit prompting with examples
- Temperature=0.3 for consistency
- Validator post-processes for grounding
- Fallback to generic response

**Prompt Template**:
```
Answer using ONLY the provided context.
Format your answer with citations: [Source 1], [Source 2], etc.
If the context doesn't contain the answer, say:
"The provided documents do not contain information about..."
```

#### Challenge 5: Distinguishing "No Info" from Errors
**Problem**: Responses like "I don't know" are valid but look like failures
**Solution**:
- Validator recognizes admission-of-ignorance phrases
- These are marked as "valid, low confidence"
- User sees appropriate guidance
- Never returns "invalid" for honest "I don't know"

**Recognized Phrases**:
- "do not contain information"
- "cannot find"
- "not available"
- "not mentioned"

---

### Known Limitations by Component

#### Document Processor
| Limitation | Impact | Notes |
|-----------|--------|-------|
| No OCR support | Can't extract from scanned PDFs | Use Tesseract for OCR |
| Image extraction | Images ignored | Suitable for text documents |
| Complex layouts | May extract incorrectly | Table parsing handles many cases |
| Encoding issues | May fail on non-UTF8 | Falls back gracefully |

#### Chunker
| Limitation | Impact | Notes |
|-----------|--------|-------|
| Fixed overlap % | Not optimal for all content | Config: 50 tokens (~10%) |
| No semantic chunking | May split at boundaries | Good enough for most docs |
| Metadata loss | Less context per chunk | Metadata stored separately |

#### Embeddings
| Limitation | Impact | Notes |
|-----------|--------|-------|
| Dimension mismatch | Requires compatible DB | OpenAI: 1536, Gemini: 768 |
| Non-English docs | Lower quality | Models trained on English |
| Expensive API calls | Cost per query | Monitor usage, add caching |
| Rate limits | API throttling | Batch efficiently |

#### Vector Store
| Limitation | Impact | Notes |
|-----------|--------|-------|
| Single machine | No distributed search | Need Pinecone/Weaviate for scale |
| No persistence across restarts | Data lost if server crashes | Mitigated by file-based storage |
| Limited to cosine similarity | May miss other relevance types | Suitable for most use cases |
| No full-text search | Can't do keyword matching | Could add hybrid search |

#### Agent Pipeline
| Limitation | Impact | Notes |
|-----------|--------|-------|
| 5-stage pipeline | Latency overhead | Necessary for quality |
| LLM API dependency | Outage blocks system | Use fallbacks, caching |
| Hallucination still possible | Wrong but grounded answers | Validator catches most cases |
| No multi-hop reasoning | Can't chain across docs | Would require agentic loop |

---

### Future Improvement Priorities

#### High Priority (1-2 weeks)
1. **Authentication**: Add JWT/OAuth
2. **Document Management**: List, delete, update endpoints
3. **Async Processing**: Background job queue
4. **Response Caching**: Redis integration

#### Medium Priority (2-4 weeks)
1. **Hybrid Search**: Vector + keyword search
2. **Multi-Collections**: Organize by project/department
3. **OCR Support**: Scanned document handling
4. **Better Chunking**: Semantic/hierarchical chunking

#### Low Priority (1+ month)
1. **Advanced UI**: React/Vue frontend
2. **Multilingual**: Support non-English docs
3. **Analytics**: Query tracking, popular questions
4. **Mobile App**: iOS/Android client

---

## Deployment Instructions

### Option 1: Local Development (Recommended for Testing)

#### Prerequisites
- Python 3.11+
- Virtual environment

#### Steps

1. **Clone repository**
```bash
git clone <repo-url>
cd genai-document-assistant
```

2. **Setup environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure .env**
```bash
cp .env.example .env
# Edit .env with your API key
```

5. **Run API server**
```bash
python -m uvicorn backend.app.main:app --reload
```

6. **Run UI** (new terminal)
```bash
streamlit run ui/streamlit_app.py
```

#### Access Points
- API: http://localhost:8000
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

### Option 2: Docker (Recommended for Production)

#### Prerequisites
- Docker 20.10+
- docker-compose 2.0+
- API key

#### Steps

1. **Clone repository**
```bash
git clone <repo-url>
cd genai-document-assistant
```

2. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your API key
```

3. **Build and run**
```bash
docker-compose up --build
```

4. **Verify services**
```bash
# Check API
curl http://localhost:8000/api/v1/health-check

# Check UI
curl http://localhost:8501
```

#### Stopping Services
```bash
docker-compose down
```

#### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f ui
```

#### Customization
Edit `docker-compose.yml` to:
- Change ports
- Add volumes
- Configure environment
- Add additional services

---

### Option 3: Cloud Deployment (AWS, GCP, Azure)

#### AWS Deployment Option 1: EC2 + Docker

1. **Launch EC2 instance**
   - Image: Ubuntu 22.04 LTS
   - Type: t3.medium or larger
   - Storage: 20GB
   - Security group: Allow ports 8000, 8501

2. **SSH to instance**
```bash
ssh -i key.pem ubuntu@instance-ip
```

3. **Install Docker**
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
```

4. **Deploy application**
```bash
git clone <repo-url>
cd genai-document-assistant
echo "LLM_API_KEY=your-key" > .env
docker-compose up -d
```

5. **Access application**
```
http://instance-ip:8000      # API
http://instance-ip:8501      # UI
```

#### AWS Deployment Option 2: ECS + Fargate

1. **Create ECR repository**
```bash
aws ecr create-repository --repository-name genai-doc-assistant
```

2. **Build and push image**
```bash
docker build -t genai-doc-assistant .
docker tag genai-doc-assistant:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-doc-assistant:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-doc-assistant:latest
```

3. **Create ECS task definition** (JSON)
```json
{
  "family": "genai-doc-assistant",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "genai-doc-assistant",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-doc-assistant:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LLM_API_KEY",
          "value": "your-key"
        }
      ]
    }
  ]
}
```

4. **Create Fargate service**
```bash
aws ecs create-service \
  --cluster genai-cluster \
  --service-name genai-doc-assistant \
  --task-definition genai-doc-assistant \
  --desired-count 1 \
  --launch-type FARGATE
```

#### GCP Deployment: Cloud Run

1. **Build image**
```bash
gcloud builds submit --tag gcr.io/PROJECT/genai-doc-assistant
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy genai-doc-assistant \
  --image gcr.io/PROJECT/genai-doc-assistant \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --set-env-vars LLM_API_KEY=your-key
```

3. **Access service**
```
https://genai-doc-assistant-xxxx-uc.a.run.app
```

#### Azure Deployment: Container Instances

1. **Build image**
```bash
az acr build --registry myregistry \
  --image genai-doc-assistant:latest .
```

2. **Deploy container**
```bash
az container create \
  --resource-group mygroup \
  --name genai-doc-assistant \
  --image myregistry.azurecr.io/genai-doc-assistant:latest \
  --memory 1 \
  --cpu 1 \
  --ports 8000 8501 \
  --environment-variables LLM_API_KEY=your-key
```

---

### Performance Tuning

#### API Server
```python
# uvicorn configuration
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    workers=4,  # Number of worker processes
    loop="uvloop",  # Fast event loop
    log_level="info"
)
```

#### Vector Database
```python
# ChromaDB configuration
client = chromadb.PersistentClient(
    path="./data/chroma",
    settings=Settings(
        chroma_db_impl="duckdb",  # Embedded DB
        allow_reset=True,
        anonymized_telemetry=False,
        is_persistent=True
    )
)
```

#### LLM API
```python
# Batch embedding requests
embeddings = embeddings_provider.embed_batch(
    texts=chunks,
    batch_size=50  # Optimal batch size
)
```

---

### Monitoring & Maintenance

#### Health Checks
```bash
# Check API
curl http://localhost:8000/api/v1/health-check

# Check UI accessibility
curl http://localhost:8501 --silent | grep "Streamlit"

# Check vector DB
python -c "
from backend.app.core.vector_store import VectorStore
vs = VectorStore()
print(vs.get_collection_stats())
"
```

#### Log Monitoring
```bash
# Docker logs
docker-compose logs -f api

# Local logs (json format)
tail -f *.log | jq .

# Error tracking
grep '"level":"ERROR"' *.log
```

#### Backup & Recovery
```bash
# Backup vector database
tar -czf chroma-backup-$(date +%Y%m%d).tar.gz ./data/chroma

# Restore backup
tar -xzf chroma-backup-20240101.tar.gz
```

---

## Quick Start

### For Impatient Users (5 Minutes)

```bash
# 1. Clone
git clone <repo-url>
cd genai-document-assistant

# 2. Setup
cp .env.example .env
# Edit .env with your API key

# 3. Run
docker-compose up

# 4. Use
# Open browser: http://localhost:8501
# Upload PDF → Ask question → Get answer with citations
```

---

## Documentation Index

### Quick References
- **[Quick Start Guide](QUICKSTART.md)** - 5-minute setup
- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - Environment variables
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Local, Docker, GitHub

### Technical Documentation
- **[Architecture](docs/ARCH.md)** - System design and data flow
- **[API Reference](docs/API.md)** - Endpoint documentation
- **[Agent Pipeline](docs/AGENTS.md)** - 5-agent detailed explanation
- **[Security](docs/SECURITY.md)** - Guardrails and safety
- **[Testing](docs/TEST_PLAN.md)** - Test strategy and coverage
- **[Deployment](docs/DEPLOYMENT.md)** - Docker and cloud deployment
- **[Limitations](docs/LIMITATIONS.md)** - Known constraints

### Project Information
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete overview
- **[Changelog](CHANGELOG.md)** - Version history
- **[Environment Report](ENV_VALIDATION_REPORT.md)** - Configuration check

---

## Conclusion

This Capstone Project demonstrates a comprehensive, production-quality Generative AI application that fully addresses all 10 core requirements:

1. ✅ Multi-format document ingestion
2. ✅ Intelligent text chunking with overlap
3. ✅ Vector embeddings generation
4. ✅ Vector database integration
5. ✅ Retrieval-Augmented Generation (RAG)
6. ✅ Multi-agent pipeline (5 agents)
7. ✅ REST API with full documentation
8. ✅ Modern web user interface
9. ✅ Security & guardrails
10. ✅ Comprehensive testing

The system is ready for educational use, internal deployment, and serves as a reference implementation for RAG-based document Q&A systems.

---

**Project Status**: ✅ Complete & Production Ready

**Last Updated**: 2024

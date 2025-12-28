# Architecture Documentation

## System Overview

The GenAI Document Assistant is a Retrieval-Augmented Generation (RAG) system that enables users to ask questions about uploaded documents. The architecture follows a layered design with clear separation of concerns.

## High-Level Architecture

```
┌─────────────┐
│  Streamlit  │ ◄─── User Interface
│     UI      │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   FastAPI   │ ◄─── REST API Layer
│   Backend   │
└──────┬──────┘
       │
       ├──► Document Processing
       │    ├── Text Extraction
       │    ├── Chunking
       │    └── Embedding
       │
       ├──► Vector Store (ChromaDB)
       │    ├── Storage
       │    └── Similarity Search
       │
       └──► Agent Pipeline
            ├── Planner
            ├── Retriever
            ├── Reasoner
            ├── Validator
            └── Responder
```

## Component Layers

### 1. Presentation Layer

**Streamlit UI** (`ui/streamlit_app.py`)
- Provides web interface for document upload and Q&A
- Communicates with API via HTTP
- Displays answers with citations and confidence scores

### 2. API Layer

**FastAPI Application** (`backend/app/main.py`, `backend/app/api/endpoints.py`)
- RESTful endpoints for document upload and question answering
- Request validation using Pydantic models
- Error handling and logging
- CORS middleware for cross-origin requests

**Endpoints:**
- `POST /api/v1/upload-document` - Upload and index documents
- `POST /api/v1/ask-question` - Ask questions about documents
- `GET /api/v1/health-check` - Check system health

### 3. Core Processing Layer

**Document Processor** (`backend/app/core/document_processor.py`)
- Extracts text from multiple file formats (PDF, TXT, CSV, XLSX, DOCX)
- Computes SHA256 hash for duplicate detection
- Preserves document metadata (filename, type, pages/sheets)

**Text Chunker** (`backend/app/core/chunker.py`)
- Splits documents into overlapping chunks
- Token-aware chunking (400-600 tokens per chunk)
- Prefers paragraph boundaries
- 10-20% overlap between chunks

**Embeddings Provider** (`backend/app/core/embeddings.py`)
- Generates vector embeddings using OpenAI or Gemini
- Abstracted interface for swapping providers
- Batch processing for efficiency

**Vector Store** (`backend/app/core/vector_store.py`)
- Wrapper around ChromaDB
- Stores embeddings with metadata
- Performs cosine similarity search
- Duplicate detection by file hash

### 4. Agent Layer

**Agent Pipeline** (`backend/app/agents/pipeline.py`)

Five sequential agents process each question:

1. **Planner Agent**
   - Validates question format
   - Detects prompt injection attempts
   - Checks if knowledge base is empty
   - Decides if retrieval is needed

2. **Retriever Agent**
   - Embeds the question
   - Performs vector similarity search
   - Returns top-k most relevant chunks
   - Includes similarity scores

3. **Reasoner Agent**
   - Builds context from retrieved chunks
   - Generates LLM prompt with instructions
   - Synthesizes evidence into draft answer
   - Enforces grounding in provided context

4. **Validator Agent**
   - Checks for prompt injection in retrieved content
   - Validates answer is grounded
   - Detects "no information" responses
   - Assesses confidence level (high/medium/low)

5. **Responder Agent**
   - Formats final answer
   - Attaches citations with metadata
   - Includes confidence score
   - Adds safety flags if needed

### 5. Utilities Layer

**Configuration** (`backend/app/config.py`)
- Environment variable management
- Settings validation using Pydantic
- Default values for all configurations

**Logger** (`backend/app/utils/logger.py`)
- Structured JSON logging
- Trace ID support for request tracking
- Configurable log levels

**Validators** (`backend/app/utils/validators.py`)
- File extension validation
- File size checks
- Prompt injection detection
- Text sanitization

## Data Flow

### Document Upload Flow

```
1. User uploads file via UI
2. API validates file type and size
3. Document processor extracts text
4. System computes file hash
5. Check for duplicates in vector store
6. If not duplicate:
   a. Chunker splits text into chunks
   b. Embeddings provider generates vectors
   c. Vector store indexes chunks with metadata
7. Return doc_id and chunk count
```

### Question Answering Flow

```
1. User submits question via UI
2. API validates question format
3. Planner agent checks for issues
4. If retrieval needed:
   a. Retriever searches vector store
   b. Returns top-k relevant chunks
5. Reasoner synthesizes answer from chunks
6. Validator checks grounding and safety
7. Responder formats final answer with citations
8. Return answer, citations, confidence, flags
```

## Data Models

### Document Chunk
```python
{
    "chunk_id": int,
    "text": str,
    "start_pos": int,
    "end_pos": int,
    "token_count": int,
    "metadata": {
        "doc_id": str,
        "filename": str,
        "file_hash": str,
        "file_type": str,
        ...
    }
}
```

### Question Response
```python
{
    "answer": str,
    "citations": [
        {
            "doc_id": str,
            "filename": str,
            "chunk_id": str,
            "score": float,
            ...
        }
    ],
    "confidence": "high" | "medium" | "low",
    "safety_flags": [str],
    "trace_id": str
}
```

## Storage

### Vector Database (ChromaDB)
- Persistent storage in `./data/chroma` directory
- Collections: documents (default)
- Metric: Cosine similarity
- Metadata stored with each embedding

### File System
- Temporary uploads: `./temp_uploads`
- Sample documents: `./sample_docs`
- Logs: stdout (JSON format)

## Security Considerations

1. **Input Validation**
   - File type whitelist
   - File size limits
   - Question length limits

2. **Prompt Injection Defense**
   - Pattern detection in questions
   - Sanitization of retrieved content
   - Instruction isolation

3. **Hallucination Prevention**
   - Validator enforces grounding
   - LLM instructed to refuse ungrounded answers
   - Citations required for claims

4. **Data Privacy**
   - No data sent to external services except LLM API
   - Duplicate detection prevents re-indexing
   - File hashes for identification

## Scalability Considerations

Current implementation is suitable for:
- Small to medium document collections (< 1000 documents)
- Low to medium query volume (< 100 QPS)
- Single-server deployment

For production scale:
- Replace ChromaDB with distributed vector store (Pinecone, Weaviate)
- Add caching layer (Redis)
- Implement async processing for uploads
- Add load balancing for API
- Use managed LLM service with higher rate limits

## Technology Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **UI Framework**: Streamlit
- **Vector DB**: ChromaDB
- **LLM Providers**: OpenAI, Google Gemini
- **Document Processing**: PyPDF2, pandas, python-docx
- **Validation**: Pydantic
- **Testing**: pytest
- **Containerization**: Docker

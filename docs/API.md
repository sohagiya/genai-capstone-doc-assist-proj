# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, no authentication is required. This is a POC implementation suitable for development and educational purposes.

## Endpoints

### 1. Upload Document

Upload and index a document into the knowledge base.

**Endpoint:** `POST /upload-document`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload

**Supported File Types:**
- PDF (`.pdf`)
- Text (`.txt`)
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)
- Word (`.docx`)

**Size Limit:** 10MB (configurable)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload-document" \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "doc_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "file_type": ".pdf",
  "num_chunks": 15,
  "message": "Document uploaded and indexed successfully",
  "trace_id": "987e6543-e21b-43d2-b654-321098765432"
}
```

**Response Fields:**
- `doc_id` (string): Unique identifier for the uploaded document
- `filename` (string): Original filename
- `file_type` (string): File extension
- `num_chunks` (integer): Number of chunks created
- `message` (string): Status message
- `trace_id` (string): Request tracking ID

**Error Responses:**

400 Bad Request - Invalid file type:
```json
{
  "detail": "File type not allowed. Allowed types: pdf,txt,csv,xlsx,doc,docx"
}
```

413 Payload Too Large - File too large:
```json
{
  "detail": "File size exceeds maximum of 10MB"
}
```

500 Internal Server Error - Processing failed:
```json
{
  "detail": "Failed to process document: <error message>"
}
```

---

### 2. Ask Question

Ask a question about uploaded documents using RAG.

**Endpoint:** `POST /ask-question`

**Request:**
- Method: `POST`
- Content-Type: `application/json`

**Request Body:**
```json
{
  "question": "What is machine learning?",
  "collection_id": "documents",
  "top_k": 5,
  "answer_style": "concise",
  "include_citations": true
}
```

**Request Fields:**
- `question` (string, required): The question to ask (1-1000 characters)
- `collection_id` (string, optional): Collection to search in (default: "documents")
- `top_k` (integer, optional): Number of chunks to retrieve (1-20, default: 5)
- `answer_style` (string, optional): Answer style - "concise", "detailed", or "bullet" (default: "concise")
- `include_citations` (boolean, optional): Include source citations (default: true)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ask-question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "top_k": 5,
    "answer_style": "concise"
  }'
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence that focuses on developing algorithms that enable computers to learn from data and improve their performance without being explicitly programmed.",
  "citations": [
    {
      "doc_id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "ai_basics.pdf",
      "page": 3,
      "sheet": null,
      "chunk_id": "123e4567-e89b-12d3-a456-426614174000_0",
      "score": 0.892
    },
    {
      "doc_id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "ai_basics.pdf",
      "page": 3,
      "sheet": null,
      "chunk_id": "123e4567-e89b-12d3-a456-426614174000_1",
      "score": 0.845
    }
  ],
  "confidence": "high",
  "safety_flags": [],
  "trace_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
  "reasoning": "Used 2 source chunks"
}
```

**Response Fields:**
- `answer` (string): The generated answer
- `citations` (array): List of source citations
  - `doc_id` (string): Document identifier
  - `filename` (string): Source filename
  - `page` (integer|null): Page number (for PDFs)
  - `sheet` (string|null): Sheet name (for Excel)
  - `chunk_id` (string): Chunk identifier
  - `score` (float): Similarity score (0-1)
- `confidence` (string): Confidence level ("high", "medium", "low")
- `safety_flags` (array): List of safety concerns (if any)
- `trace_id` (string): Request tracking ID
- `reasoning` (string|null): Internal reasoning notes

**Special Responses:**

No documents uploaded:
```json
{
  "answer": "No documents have been uploaded yet. Please upload documents before asking questions.",
  "citations": [],
  "confidence": "low",
  "safety_flags": ["empty_knowledge_base"],
  ...
}
```

Answer not found:
```json
{
  "answer": "I don't see that in the uploaded documents. Could you upload relevant documents or rephrase your question?",
  "citations": [],
  "confidence": "low",
  ...
}
```

Prompt injection detected:
```json
{
  "answer": "I cannot process this question as it contains potentially unsafe patterns.",
  "citations": [],
  "confidence": "low",
  "safety_flags": ["prompt_injection"],
  ...
}
```

**Error Responses:**

400 Bad Request - Invalid question:
```json
{
  "detail": "Question cannot be empty"
}
```

422 Validation Error - Schema validation failed:
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

Check API and vector database health status.

**Endpoint:** `GET /health-check`

**Request:**
- Method: `GET`
- No parameters

**Example:**
```bash
curl http://localhost:8000/api/v1/health-check
```

**Response:**
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

**Response Fields:**
- `status` (string): Overall health status ("healthy" or "unhealthy")
- `vector_db_connected` (boolean): Vector database connectivity
- `collection_stats` (object): Statistics about the document collection
  - `collection_name` (string): Name of the collection
  - `total_chunks` (integer): Total number of indexed chunks

**Unhealthy Response:**
```json
{
  "status": "unhealthy",
  "vector_db_connected": false,
  "collection_stats": {}
}
```

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints and schemas
- Try out API calls directly
- See request/response examples
- Download OpenAPI specification

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider adding rate limiting middleware.

## CORS

CORS is enabled for all origins in the current configuration. For production, restrict to specific origins in [backend/app/main.py](backend/app/main.py).

## Trace IDs

Every request generates a unique `trace_id` for logging and debugging. Include this ID when reporting issues.

## Content Types

- Requests: `application/json` (except file uploads which use `multipart/form-data`)
- Responses: `application/json`

## HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid input
- `413 Payload Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

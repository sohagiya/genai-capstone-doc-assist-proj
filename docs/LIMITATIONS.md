# Limitations and Assumptions

## Overview

This document outlines known limitations, assumptions, and trade-offs in the GenAI Document Assistant POC.

## Architectural Limitations

### 1. Vector Database

**Current: ChromaDB (file-based, single-node)**

Limitations:
- Not designed for multi-writer scenarios
- Limited scalability (< 10M documents)
- No built-in replication or high availability
- File-based storage (not suitable for distributed systems)

**Impact:**
- Cannot run multiple API instances with shared writes
- Limited to single-server deployment
- No automatic failover

**Mitigation:**
- Acceptable for POC and small deployments
- For production: migrate to Pinecone, Weaviate, or Milvus
- Code abstracted via `VectorStore` class for easy swapping

### 2. LLM Provider Dependency

**Current: OpenAI or Gemini API**

Limitations:
- Requires internet connection
- Data sent to third-party service
- Subject to provider rate limits
- Costs per API call
- No offline operation

**Impact:**
- Cannot work in air-gapped environments
- Privacy concerns for sensitive documents
- Variable latency based on API performance
- Ongoing operational costs

**Mitigation:**
- Use provider with strong privacy guarantees
- For sensitive data: consider on-premises LLM (e.g., Llama, Mistral)
- Implement caching to reduce API calls
- Monitor and cap usage

### 3. No Authentication/Authorization

**Current: Open API, no user management**

Limitations:
- All users share same knowledge base
- No document-level access control
- No user isolation
- No audit trail per user

**Impact:**
- Not suitable for multi-tenant scenarios
- Cannot restrict document access
- Privacy and compliance risks

**Mitigation:**
- Acceptable for POC and single-user scenarios
- For production: add JWT/OAuth authentication
- Implement role-based access control (RBAC)
- Add per-user document collections

### 4. Single Collection

**Current: All documents in one "documents" collection**

Limitations:
- Cannot organize documents by project/topic
- All questions search all documents
- No way to scope queries to subset

**Impact:**
- Less relevant results as document count grows
- No multi-tenancy support

**Mitigation:**
- Acceptable for POC
- Future: support multiple collections
- Allow users to specify collection in queries

## Functional Limitations

### 5. File Format Support

**Supported:** PDF, TXT, CSV, XLSX, DOCX

Limitations:
- No images in PDFs (text only)
- No OCR for scanned documents
- Limited formatting preservation
- No tables/charts extraction from PDF
- CSV/XLSX converted to text (loses structure)

**Impact:**
- Scanned documents not readable
- Complex layouts may lose meaning
- Tabular data flattened

**Mitigation:**
- Encourage text-based or searchable PDFs
- Pre-process scanned docs with OCR
- Future: add OCR support (Tesseract)
- Use specialized parsers for tables

### 6. Document Size Limit

**Current: 10MB max upload**

Limitations:
- Large documents rejected
- No streaming upload
- Memory constraints during processing

**Impact:**
- Cannot process very large files
- Multi-file uploads needed for large datasets

**Mitigation:**
- Configurable limit (MAX_UPLOAD_MB)
- Split large documents before upload
- Future: implement chunked/streaming upload

### 7. Chunking Strategy

**Current: Fixed token target (500), paragraph-based**

Limitations:
- May break semantic units
- Fixed size doesn't adapt to content
- No semantic boundary detection
- Overlap may duplicate information

**Impact:**
- Some questions may span chunk boundaries
- Larger chunks = fewer but less precise
- Smaller chunks = more but may miss context

**Mitigation:**
- 400-600 token range balances precision/recall
- 10-20% overlap helps continuity
- Future: semantic chunking (sentence embeddings)

### 8. Search Quality

**Current: Pure vector similarity (cosine distance)**

Limitations:
- No keyword matching
- No BM25 hybrid search
- No query expansion
- No re-ranking

**Impact:**
- May miss exact keyword matches
- Relies solely on semantic similarity
- Less effective for factual lookups (names, dates)

**Mitigation:**
- Embeddings generally good for semantic search
- Future: hybrid search (vector + BM25)
- Add query expansion via LLM

### 9. Answer Generation

**Current: Single LLM call with top-k chunks**

Limitations:
- No iterative refinement
- No multi-hop reasoning
- Context window limited (top-k chunks)
- No answer verification via multiple strategies

**Impact:**
- Complex questions requiring synthesis may fail
- Limited to information in top-k chunks
- No self-correction

**Mitigation:**
- Increase top_k for broader context
- Future: iterative questioning, chain-of-thought
- Add answer verification agent

### 10. Citation Granularity

**Current: Chunk-level citations**

Limitations:
- Cannot cite specific sentence
- Cannot highlight exact supporting text
- Page numbers approximate (for PDFs)

**Impact:**
- User must read entire chunk to verify
- Less precise attribution

**Mitigation:**
- Acceptable for POC
- Future: sentence-level citation
- Add text highlighting in UI

## Security Limitations

### 11. Prompt Injection Defense

**Current: Pattern-based detection**

Limitations:
- Only detects known patterns
- Can be bypassed with novel techniques
- No semantic analysis of injection attempts

**Impact:**
- Not foolproof
- Sophisticated attacks may succeed

**Mitigation:**
- Multiple layers of defense (Planner + Validator)
- LLM instructed to ignore commands in context
- Future: ML-based injection detection

### 12. No Encryption at Rest

**Current: Vector DB and uploads stored in plaintext**

Limitations:
- Data readable if storage compromised
- No protection against disk theft

**Impact:**
- Privacy risk for sensitive documents

**Mitigation:**
- Acceptable for POC
- For production: encrypt vector DB
- Use encrypted volumes (LUKS, dm-crypt)

### 13. No Rate Limiting

**Current: Unlimited requests**

Limitations:
- Vulnerable to abuse/DoS
- No per-user quotas
- No cost control

**Impact:**
- API can be overwhelmed
- Unexpected LLM API costs

**Mitigation:**
- Acceptable for POC
- For production: add rate limiting middleware
- Implement per-user quotas

## Performance Limitations

### 14. Synchronous Processing

**Current: Upload blocks until indexing completes**

Limitations:
- Large documents slow to upload
- No background processing
- Client must wait for full process

**Impact:**
- Poor UX for large files
- Timeout risk on slow connections

**Mitigation:**
- Acceptable for POC
- Future: async upload with job queue
- Return job ID, poll for status

### 15. No Caching

**Current: Every query regenerates answer**

Limitations:
- Repeated questions re-compute
- No deduplication
- Higher latency and cost

**Impact:**
- Inefficient for common questions
- Higher LLM API costs

**Mitigation:**
- Acceptable for POC
- Future: cache question-answer pairs
- Use Redis or in-memory cache

### 16. Single-Threaded Question Processing

**Current: Questions processed sequentially**

Limitations:
- Concurrent questions not parallelized
- Limited throughput

**Impact:**
- Low query volume supported

**Mitigation:**
- Acceptable for POC
- For production: use async FastAPI handlers
- Add worker pool

## Data Quality Limitations

### 17. No Document Validation

**Current: Minimal validation beyond file type**

Limitations:
- No content quality checks
- No language detection
- No encoding validation
- Corrupted files may partially index

**Impact:**
- Garbage in, garbage out
- Mixed-language documents may confuse embeddings

**Mitigation:**
- Acceptable for POC
- Future: add content validation
- Detect and warn on language mismatches

### 18. No Duplicate Detection (Content)

**Current: Only hash-based duplicate detection**

Limitations:
- Same content in different files not detected
- Minor changes bypass deduplication
- No near-duplicate detection

**Impact:**
- Redundant information indexed
- Inflated chunk count

**Mitigation:**
- Hash-based detection catches exact duplicates
- Future: content-based similarity detection

### 19. No Document Metadata Enrichment

**Current: Basic metadata only (filename, type, pages)**

Limitations:
- No author extraction
- No creation date
- No topic classification
- No summary generation

**Impact:**
- Limited filtering/search capabilities
- No document organization by metadata

**Mitigation:**
- Acceptable for POC
- Future: extract metadata from file properties
- Add auto-tagging via LLM

## Usability Limitations

### 20. No Document Management

**Current: No list, delete, or update operations**

Limitations:
- Cannot view uploaded documents
- Cannot delete specific documents
- Cannot update documents
- No search by filename

**Impact:**
- Documents accumulate indefinitely
- No way to clean up mistakes

**Mitigation:**
- Acceptable for POC
- Future: add document management endpoints
- Add UI for document library

### 21. No Question History

**Current: Questions not saved**

Limitations:
- No conversation history
- Cannot revisit past answers
- No follow-up questions

**Impact:**
- Each question isolated
- Cannot refine based on previous

**Mitigation:**
- Acceptable for POC
- Future: store question/answer history
- Add conversational context

### 22. Basic UI

**Current: Simple Streamlit interface**

Limitations:
- Limited interactivity
- No real-time updates
- Basic styling
- No mobile optimization

**Impact:**
- Functional but not polished

**Mitigation:**
- Acceptable for POC
- For production: rebuild UI in React/Vue
- Add rich formatting, highlighting, etc.

## Operational Limitations

### 23. No Monitoring/Telemetry

**Current: Basic JSON logging only**

Limitations:
- No metrics collection
- No alerting
- No performance dashboards
- No error tracking

**Impact:**
- Difficult to diagnose issues in production
- No visibility into usage patterns

**Mitigation:**
- Acceptable for POC
- For production: add Prometheus, Grafana
- Integrate with APM (DataDog, New Relic)

### 24. No Backup Strategy

**Current: Manual backup only**

Limitations:
- No automated backups
- No point-in-time recovery
- Risk of data loss

**Impact:**
- Vector DB loss requires re-indexing all documents

**Mitigation:**
- Acceptable for POC
- For production: automated daily backups
- Use versioned storage (S3 with versioning)

### 25. No Health Monitoring

**Current: Single endpoint, basic checks**

Limitations:
- No component-level health
- No dependency checks (LLM API, etc.)
- No readiness vs liveness distinction

**Impact:**
- Difficult to diagnose partial failures

**Mitigation:**
- Acceptable for POC
- For production: detailed health checks
- Separate readiness/liveness endpoints

## Assumptions

### User Assumptions

1. **Users have basic technical knowledge**
   - Can use command line
   - Understand API concepts
   - Can configure environment variables

2. **Documents are in supported formats**
   - Text-based (not scanned/images)
   - English language (or LLM-supported language)
   - Reasonable file sizes (< 10MB)

3. **Questions are in natural language**
   - Complete sentences preferred
   - Clear and specific
   - Related to uploaded documents

### Environmental Assumptions

1. **Stable internet connection**
   - For LLM API calls
   - For initial setup (pip install)

2. **Sufficient compute resources**
   - 4GB+ RAM
   - Modern CPU
   - SSD storage

3. **Trusted environment**
   - Local deployment or secured server
   - No malicious users
   - No sensitive/regulated data (unless additional security added)

### Data Assumptions

1. **Documents are factual**
   - Contain accurate information
   - Not contradictory
   - Trustworthy sources

2. **Documents are self-contained**
   - Don't require external references
   - Context within document

3. **No multimedia content**
   - Text-only
   - No images, videos, audio

## Trade-offs Made

### Simplicity vs. Features

**Chose:** Simplicity for POC
- Basic auth (none) vs. complex RBAC
- Single collection vs. multi-tenant
- Synchronous vs. async processing

**Rationale:** Educational project, clear code > advanced features

### Cost vs. Quality

**Chose:** Quality (good LLM) with configurable cost
- Default: gpt-4o-mini (balance)
- Option: switch to cheaper models
- Option: on-premises LLM

**Rationale:** Better answers worth cost for POC; production can optimize

### Scalability vs. Complexity

**Chose:** Simple single-node for POC
- ChromaDB vs. distributed vector DB
- Single server vs. microservices

**Rationale:** Sufficient for POC; production can scale out

### Precision vs. Recall

**Chose:** Balanced via top-k=5
- Fewer chunks = faster, less context
- More chunks = slower, better recall

**Rationale:** 5 chunks generally sufficient; user can adjust

## Future Work

Priority improvements:

1. **High Priority**
   - Add authentication/authorization
   - Implement document management (list, delete)
   - Add hybrid search (vector + keyword)
   - Improve error handling

2. **Medium Priority**
   - Async upload processing
   - Answer caching
   - Multi-collection support
   - Better chunking strategy

3. **Low Priority**
   - OCR support
   - Multilingual support
   - Advanced UI
   - Mobile app

## Summary

This POC is designed for **educational purposes** and **small-scale deployment**. It demonstrates core RAG concepts with agent-based reasoning but has intentional limitations to keep the codebase simple and maintainable.

For **production use**, address:
- Authentication & authorization
- Scalable vector database
- Comprehensive security
- Monitoring & alerting
- Data encryption
- Performance optimization

The modular architecture makes it relatively easy to upgrade components (vector DB, LLM provider, UI) without major rewrites.

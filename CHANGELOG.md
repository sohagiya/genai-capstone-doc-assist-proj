# Changelog

All notable changes to the GenAI Document Assistant project.

## [1.0.1] - 2025-12-28

### Bug Fixes

#### CSV/Excel Metadata Queries (Fixed)
- **Issue**: CSV/Excel files didn't include metadata in embedded text, so AI couldn't answer questions about row counts, column counts, or file structure
- **Fix**:
  - Added metadata summary at beginning of extracted text for CSV files
  - Added metadata summary at beginning of extracted text for Excel files
  - Metadata includes: total rows, total columns, column names, sheet details (for Excel)
  - Enables AI to answer questions like "how many rows are in this file?"
  - Supports data analysis queries with full context

## [1.0.0] - 2025-12-28

### Initial Release

Complete GenAI Document Assistant capstone project with RAG-based Q&A system.

### Features

#### Core Functionality
- **Multi-format Document Support**: PDF, TXT, CSV, XLSX, DOCX
- **Document Management**: Upload, view, delete individual documents, clear all
- **Semantic Search**: Vector-based similarity using ChromaDB and OpenAI embeddings
- **Agent Pipeline**: 5-stage processing (Planner → Retriever → Reasoner → Validator → Responder)
- **Smart Citations**: Document-grouped sources with relevance scores

#### API (FastAPI)
- **6 REST Endpoints**:
  - `POST /api/v1/upload-document` - Upload and process documents
  - `POST /api/v1/ask-question` - Ask questions with AI-powered answers
  - `GET /api/v1/list-documents` - List all uploaded documents
  - `DELETE /api/v1/delete-document/{doc_id}` - Delete specific document
  - `POST /api/v1/clear-all-documents` - Clear all documents
  - `GET /api/v1/health-check` - System health status
- OpenAPI documentation at `/docs`
- Structured JSON logging with trace IDs
- Input validation and guardrails

#### User Interface (Streamlit)
- **Single-page layout** with side-by-side panels
- **Left Panel**: Document upload and management
- **Right Panel**: Question input and answer display
- **Sidebar**: Settings (top_k, answer style), system controls
- Real-time document list with delete buttons
- Citation display grouped by source document
- Confidence indicators and safety warnings

#### Security & Guardrails
- Prompt injection detection
- Hallucination prevention
- Input validation (file type, size, content)
- API key protection (not in git)
- SHA256 duplicate detection

#### Deployment
- Docker support with docker-compose
- Git version control ready
- Comprehensive documentation
- Setup and run scripts for Windows/Linux

### Technical Stack
- **Backend**: FastAPI 0.109.0, Python 3.11+
- **Frontend**: Streamlit 1.30.0
- **Vector DB**: ChromaDB 0.4.22
- **LLM**: OpenAI GPT-4o-mini (or Gemini)
- **Embeddings**: text-embedding-3-small
- **Document Processing**: PyPDF2, python-docx, pandas, openpyxl

### Project Statistics
- **Total Files**: 51 committed to Git
- **Lines of Code**: 7,600+
- **Python Packages**: 17 dependencies
- **Documentation**: 12 comprehensive guides
- **Test Files**: 4 test suites

### Bug Fixes

#### XLSX/CSV Upload Issues (Fixed)
- **Issue**: Large Excel files exceeded OpenAI token limits (2.2M tokens requested, 300K max)
- **Issue**: File lock errors preventing cleanup after upload
- **Fix**:
  - Limited Excel sheets to 1000 rows max per sheet
  - Truncated cell values to 500 characters
  - Limited total extracted text to 100K characters
  - Properly close Excel file handles in finally block
  - Added content truncation warnings in logs

#### Citation Display Confusion (Fixed)
- **Issue**: Showed "3 sources" when 1 document had 3 chunks
- **Fix**:
  - Group citations by source document
  - Display "X document(s) used | Y chunk(s) retrieved"
  - Show average relevance per document
  - Expandable details per document with chunk scores

#### Security Issue (Fixed)
- **Issue**: Real OpenAI API key exposed in `.env.example`
- **Fix**: Replaced with placeholder `your-api-key-here`

#### Document Persistence (Fixed)
- **Issue**: All documents persisted across sessions, affecting new queries
- **Fix**:
  - Added document management endpoints
  - UI controls to view and delete documents
  - Clear all functionality

#### UI/UX Improvements (Fixed)
- **Issue**: Tab-based UI required switching between upload and Q&A
- **Fix**: Completely redesigned to single-page 2-column layout

### Documentation

#### Quick Start Guides
- `README.md` - Main documentation with badges and stats
- `QUICKSTART.md` - 5-minute setup guide
- `DEPLOYMENT_GUIDE.md` - Local, Docker, and GitHub deployment
- `CONFIGURATION_GUIDE.md` - Environment variables reference
- `CHANGELOG.md` - This file

#### Technical Documentation
- `docs/ARCH.md` - Architecture and data flow
- `docs/API.md` - API endpoints and schemas
- `docs/AGENTS.md` - Agent pipeline details
- `docs/SECURITY.md` - Security measures
- `docs/TEST_PLAN.md` - Testing strategy
- `docs/DEPLOYMENT.md` - Docker deployment
- `docs/LIMITATIONS.md` - Known limitations

#### Project Reports
- `PROJECT_SUMMARY.md` - Complete project overview
- `ENV_VALIDATION_REPORT.md` - Configuration validation results

### Git Commits

1. **Initial commit**: Complete project structure (51 files, 7,600+ lines)
2. **Documentation update**: GitHub deployment instructions, updated README
3. **Bug fix**: XLSX/CSV file upload issues resolved

### Known Limitations

1. **File Size Limits**:
   - Max upload: 10MB (configurable)
   - Excel files limited to 1000 rows per sheet
   - CSV files limited to 1000 rows total
   - Total extracted text limited to 100K characters

2. **LLM Token Limits**:
   - Chunks limited to 500 tokens each
   - Very large documents automatically truncated
   - Warning messages shown when truncation occurs

3. **Vector Database**:
   - Local ChromaDB (not distributed)
   - No backup/restore built-in
   - Data persists in `./data/chroma`

4. **Deployment**:
   - Streamlit Community Cloud not supported (requires backend+frontend)
   - Recommended: Local deployment or Docker
   - Cloud deployment requires platform like Railway or Render

### Future Enhancements (Out of Scope)

- User authentication and multi-tenancy
- Document versioning
- Advanced analytics dashboard
- Support for more file formats (PPT, images with OCR)
- Distributed vector database (Pinecone, Weaviate)
- Batch processing for multiple documents
- Export answers to PDF/Word
- REST API rate limiting
- Webhook notifications

### License

Educational use only - College capstone project

### Contributors

**Capstone Project Team**
- College of Professional Studies
- Course: Advanced Generative AI

### Acknowledgments

- OpenAI for GPT-4 and embeddings API
- ChromaDB team for vector database
- FastAPI and Streamlit communities
- All open-source contributors

---

**Version**: 1.0.0
**Release Date**: December 28, 2025
**Status**: Production-ready for demonstration

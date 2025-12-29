"""FastAPI endpoint handlers"""
import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.models import (
    AskQuestionRequest,
    AskQuestionResponse,
    UploadDocumentResponse,
    HealthCheckResponse,
    Citation
)
from backend.app.config import settings
from backend.app.core.document_processor import DocumentProcessor
from backend.app.core.chunker import TextChunker
from backend.app.core.vector_store import VectorStore
from backend.app.agents.pipeline import AgentPipeline
from backend.app.utils.validators import validate_file_extension, validate_file_size, validate_question
from backend.app.utils.logger import logger

router = APIRouter()

# Initialize components
vector_store = VectorStore(collection_name="documents")
agent_pipeline = AgentPipeline(vector_store)
document_processor = DocumentProcessor()
text_chunker = TextChunker(target_tokens=500, overlap_tokens=50)


@router.post("/upload-document", response_model=UploadDocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    Supports: PDF, TXT, CSV, XLSX, DOCX
    """
    trace_id = str(uuid.uuid4())
    logger.info(f"Upload request received", extra={"trace_id": trace_id})

    try:
        # Validate file extension
        if not validate_file_extension(file.filename, settings.allowed_extensions_list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {settings.allowed_extensions}"
            )

        # Save uploaded file to uploads directory (for data preview)
        uploads_dir = Path("./uploads")
        uploads_dir.mkdir(exist_ok=True)
        saved_file_path = uploads_dir / file.filename

        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Validate file size
        file_size = os.path.getsize(saved_file_path)
        if not validate_file_size(file_size, settings.max_upload_bytes):
            os.remove(saved_file_path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum of {settings.max_upload_mb}MB"
            )

        # Process document
        try:
            processed_doc = document_processor.process_document(str(saved_file_path), file.filename)
        except Exception as e:
            os.remove(saved_file_path)
            logger.error(f"Document processing failed: {str(e)}", extra={"trace_id": trace_id})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {str(e)}"
            )

        # Check for duplicate based on hash
        file_hash = processed_doc["metadata"]["file_hash"]
        existing_doc_id = vector_store.check_document_exists(file_hash)

        if existing_doc_id:
            # Keep the file for data preview even if duplicate
            logger.info(f"Duplicate document detected: {file_hash}", extra={"trace_id": trace_id})
            return UploadDocumentResponse(
                doc_id=existing_doc_id,
                filename=file.filename,
                file_type=processed_doc["metadata"]["file_type"],
                num_chunks=0,
                message="Document already exists (duplicate detected)",
                trace_id=trace_id
            )

        # Chunk the text
        chunks = text_chunker.chunk_text(
            processed_doc["text"],
            metadata=processed_doc["metadata"]
        )

        # Check if any chunks were created
        if not chunks or len(chunks) == 0:
            os.remove(saved_file_path)
            logger.warning(f"No text chunks created from document: {file.filename}", extra={"trace_id": trace_id})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not extract text from document. The file may be empty, scanned images without OCR, password-protected, or corrupted."
            )

        # Generate document ID and add to vector store
        doc_id = str(uuid.uuid4())
        vector_store.add_documents(chunks, doc_id)

        # Keep the file saved for data preview

        logger.info(f"Document uploaded successfully: {doc_id}", extra={"trace_id": trace_id})

        return UploadDocumentResponse(
            doc_id=doc_id,
            filename=file.filename,
            file_type=processed_doc["metadata"]["file_type"],
            num_chunks=len(chunks),
            message="Document uploaded and indexed successfully",
            trace_id=trace_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/ask-question", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest):
    """
    Ask a question based on uploaded documents
    Returns answer with citations
    """
    trace_id = str(uuid.uuid4())
    logger.info(f"Question request received", extra={"trace_id": trace_id})

    try:
        # Validate question
        is_valid, error_msg = validate_question(request.question)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Process through agent pipeline
        result = agent_pipeline.process_question(
            question=request.question,
            top_k=request.top_k,
            answer_style=request.answer_style
        )

        # Format citations
        citations = []
        if request.include_citations:
            citations = [Citation(**c) for c in result.get("citations", [])]

        response = AskQuestionResponse(
            answer=result["answer"],
            citations=citations,
            confidence=result.get("confidence", "medium"),
            safety_flags=result.get("safety_flags", []),
            trace_id=trace_id,
            reasoning=result.get("reasoning")
        )

        logger.info(f"Question answered successfully", extra={"trace_id": trace_id})
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your question"
        )


@router.get("/list-documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = vector_store.list_all_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.delete("/delete-document/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a specific document and its chunks"""
    try:
        vector_store.delete_document(doc_id)
        return {"message": f"Document {doc_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.post("/clear-all-documents")
async def clear_all_documents():
    """Clear all documents from the vector store"""
    try:
        count = vector_store.clear_all_documents()
        return {"message": f"Cleared {count} documents successfully"}
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear documents"
        )


@router.get("/get-data-preview/{doc_id}")
async def get_data_preview(doc_id: str, num_rows: int = 100):
    """
    Get a tabular preview of CSV/Excel data
    """
    try:
        import pandas as pd
        from pathlib import Path

        # Get document metadata
        documents = vector_store.list_all_documents()
        doc = next((d for d in documents if d['doc_id'] == doc_id), None)

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found"
            )

        # Check if it's a CSV or Excel file
        file_type = doc.get('file_type', '')
        if file_type not in ['.csv', '.xlsx', '.xls']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data preview only supported for CSV/Excel files, got {file_type}"
            )

        # Load the data from uploads directory
        filename = doc.get('filename', '')
        file_path = Path(f"./uploads/{filename}")

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source file not found: {filename}"
            )

        # Read the file
        if file_type == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Get preview
        preview_df = df.head(num_rows)

        # Get column info
        columns_info = []
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].notna().sum()),
                "null": int(df[col].isna().sum())
            }

            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["stats"] = {
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                }
            else:
                col_info["unique_values"] = int(df[col].nunique())

            columns_info.append(col_info)

        return {
            "doc_id": doc_id,
            "filename": filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "preview_rows": len(preview_df),
            "columns": columns_info,
            "data": preview_df.to_dict(orient='records')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data preview: {str(e)}"
        )


@router.get("/health-check", response_model=HealthCheckResponse)
async def health_check():
    """Check API and vector database health"""
    try:
        # Check vector store connection
        is_healthy = vector_store.health_check()
        stats = vector_store.get_collection_stats()

        return HealthCheckResponse(
            status="healthy" if is_healthy else "unhealthy",
            vector_db_connected=is_healthy,
            collection_stats=stats
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            vector_db_connected=False,
            collection_stats={}
        )

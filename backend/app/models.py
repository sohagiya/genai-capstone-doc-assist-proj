"""Pydantic models for API request/response schemas"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    """Request model for asking a question"""
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    collection_id: str = Field(default="documents", description="Collection to search in")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    answer_style: str = Field(default="concise", description="Answer style: concise, detailed, or bullet")
    include_citations: bool = Field(default=True, description="Whether to include citations")


class Citation(BaseModel):
    """Citation information for a source"""
    doc_id: str
    filename: str
    page: Optional[int] = None
    sheet: Optional[int] = None
    chunk_id: str
    score: float


class AskQuestionResponse(BaseModel):
    """Response model for question answering"""
    answer: str
    citations: List[Citation]
    confidence: str = Field(..., description="Confidence level: high, medium, or low")
    safety_flags: List[str] = Field(default_factory=list)
    trace_id: str
    reasoning: Optional[str] = None


class UploadDocumentResponse(BaseModel):
    """Response model for document upload"""
    doc_id: str
    filename: str
    file_type: str
    num_chunks: int
    message: str
    trace_id: str


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str
    vector_db_connected: bool
    collection_stats: Dict[str, Any]

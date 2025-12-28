"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.endpoints import router
from backend.app.config import settings
from backend.app.utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="GenAI Document Assistant API",
    description="RAG-based document Q&A system with agent pipeline",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting GenAI Document Assistant API")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector DB: {settings.vector_db_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down GenAI Document Assistant API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GenAI Document Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/v1/upload-document",
            "ask": "/api/v1/ask-question",
            "health": "/api/v1/health-check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

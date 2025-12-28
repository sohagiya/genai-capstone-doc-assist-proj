"""Configuration management using environment variables"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    llm_api_key: str = Field(default="", env="LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    embeddings_model: str = Field(default="text-embedding-3-small", env="EMBEDDINGS_MODEL")

    # Vector Database
    vector_db_dir: str = Field(default="./data/chroma", env="VECTOR_DB_DIR")

    # Upload Configuration
    max_upload_mb: int = Field(default=10, env="MAX_UPLOAD_MB")
    allowed_extensions: str = Field(default="pdf,txt,csv,xlsx,doc,docx", env="ALLOWED_EXTENSIONS")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Return allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        """Return max upload size in bytes"""
        return self.max_upload_mb * 1024 * 1024


# Global settings instance
settings = Settings()

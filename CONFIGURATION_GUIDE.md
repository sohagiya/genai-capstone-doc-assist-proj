# Configuration Guide

## Environment Variables Reference

This guide explains all configuration options and how they're used in the code.

## Configuration Flow

```
.env file
    ↓
backend/app/config.py (Settings class)
    ↓
Imported by all modules via: from backend.app.config import settings
    ↓
Used in: embeddings.py, vector_store.py, endpoints.py, main.py
```

## File: `.env` (You must create this)

**Location**: Project root directory

**How to create**:
```bash
cp .env.example .env
```

Then edit `.env` with your actual values.

## All Environment Variables

### 1. LLM_PROVIDER
- **Description**: Which LLM service to use
- **Valid values**: `openai` or `gemini`
- **Default**: `openai`
- **Required**: Yes
- **Used in**:
  - `backend/app/core/embeddings.py` - Lines 13, 16, 18, 35, 37
  - Determines which API to call for embeddings and completions

**Example**:
```env
LLM_PROVIDER=openai
```

### 2. LLM_API_KEY
- **Description**: API key for your LLM provider
- **Valid values**: String (starts with `sk-` for OpenAI)
- **Default**: Empty string (will fail if not set)
- **Required**: Yes
- **Used in**:
  - `backend/app/core/embeddings.py` - Lines 17, 19, 48, 83, 85, 107
  - Passed to OpenAI or Gemini client for authentication

**OpenAI Example**:
```env
LLM_API_KEY=sk-proj-abc123xyz...
```

**Gemini Example**:
```env
LLM_API_KEY=AIzaSy...
```

**⚠️ Security**: NEVER commit this to git! The `.env` file is in `.gitignore`.

### 3. LLM_MODEL
- **Description**: LLM model name for text generation
- **Valid values**: Any valid model name from your provider
- **Default**: `gpt-4o-mini`
- **Required**: Yes
- **Used in**:
  - `backend/app/core/embeddings.py` - Line 80
  - `backend/app/agents/pipeline.py` - Via LLMProvider

**OpenAI Options**:
```env
LLM_MODEL=gpt-4o-mini          # Recommended (fast, cheap)
LLM_MODEL=gpt-4o               # More capable, more expensive
LLM_MODEL=gpt-3.5-turbo        # Cheaper, less capable
```

**Gemini Options**:
```env
LLM_MODEL=gemini-1.5-flash     # Fast and efficient
LLM_MODEL=gemini-1.5-pro       # More capable
```

### 4. EMBEDDINGS_MODEL
- **Description**: Model for generating vector embeddings
- **Valid values**: Valid embedding model from provider
- **Default**: `text-embedding-3-small`
- **Required**: Yes
- **Used in**:
  - `backend/app/core/embeddings.py` - Line 14
  - Creates embeddings for documents and queries

**OpenAI Options**:
```env
EMBEDDINGS_MODEL=text-embedding-3-small   # Recommended (512 dims)
EMBEDDINGS_MODEL=text-embedding-3-large   # Better quality (3072 dims)
EMBEDDINGS_MODEL=text-embedding-ada-002   # Legacy
```

**Gemini Options**:
```env
EMBEDDINGS_MODEL=models/embedding-001     # Standard
```

### 5. VECTOR_DB_DIR
- **Description**: Directory to store ChromaDB vector database
- **Valid values**: Any valid directory path
- **Default**: `./data/chroma`
- **Required**: No (will use default)
- **Used in**:
  - `backend/app/core/vector_store.py` - Line 22
  - Stores embedded document chunks

**Example**:
```env
VECTOR_DB_DIR=./data/chroma              # Relative path (default)
VECTOR_DB_DIR=/var/lib/genai/chroma      # Absolute path
```

**Note**: Directory will be created automatically if it doesn't exist.

### 6. MAX_UPLOAD_MB
- **Description**: Maximum file upload size in megabytes
- **Valid values**: Integer (1-100 recommended)
- **Default**: `10`
- **Required**: No
- **Used in**:
  - `backend/app/config.py` - Line 21, property `max_upload_bytes`
  - `backend/app/api/endpoints.py` - Via `settings.max_upload_bytes`

**Example**:
```env
MAX_UPLOAD_MB=10     # 10 MB limit
MAX_UPLOAD_MB=50     # 50 MB limit (for larger files)
```

### 7. ALLOWED_EXTENSIONS
- **Description**: Comma-separated list of allowed file extensions
- **Valid values**: File extensions without dots
- **Default**: `pdf,txt,csv,xlsx,doc,docx`
- **Required**: No
- **Used in**:
  - `backend/app/config.py` - Line 22, property `allowed_extensions_list`
  - `backend/app/api/endpoints.py` - Via `settings.allowed_extensions_list`
  - `backend/app/utils/validators.py` - File validation

**Example**:
```env
ALLOWED_EXTENSIONS=pdf,txt,csv,xlsx,doc,docx   # Default
ALLOWED_EXTENSIONS=pdf,txt                     # Only PDF and TXT
```

### 8. API_HOST
- **Description**: Host address for the API server
- **Valid values**: IP address or hostname
- **Default**: `0.0.0.0` (all interfaces)
- **Required**: No
- **Used in**:
  - `backend/app/main.py` - Line 57
  - Determines which network interfaces the API listens on

**Example**:
```env
API_HOST=0.0.0.0      # All interfaces (default)
API_HOST=127.0.0.1    # Localhost only
API_HOST=localhost    # Localhost only
```

### 9. API_PORT
- **Description**: Port number for the API server
- **Valid values**: Integer (1024-65535)
- **Default**: `8000`
- **Required**: No
- **Used in**:
  - `backend/app/main.py` - Line 58
  - Port where the FastAPI server listens

**Example**:
```env
API_PORT=8000    # Default
API_PORT=8080    # Alternative
```

### 10. LOG_LEVEL
- **Description**: Logging verbosity level
- **Valid values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default**: `INFO`
- **Required**: No
- **Used in**:
  - `backend/app/utils/logger.py` - Via settings
  - Controls how much logging output is shown

**Example**:
```env
LOG_LEVEL=INFO       # Normal (default)
LOG_LEVEL=DEBUG      # Verbose (for troubleshooting)
LOG_LEVEL=WARNING    # Less verbose
```

## Complete .env Template

```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small

# Vector Database
VECTOR_DB_DIR=./data/chroma

# Upload Configuration
MAX_UPLOAD_MB=10
ALLOWED_EXTENSIONS=pdf,txt,csv,xlsx,doc,docx

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

## How Configuration is Loaded

### Step 1: Pydantic Settings Class

File: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    llm_api_key: str = Field(default="", env="LLM_API_KEY")
    # ... other fields ...

    class Config:
        env_file = ".env"        # Load from .env file
        case_sensitive = False   # Case-insensitive matching

# Global instance
settings = Settings()
```

### Step 2: Import in Modules

All modules that need config import it:

```python
from backend.app.config import settings

# Then use:
api_key = settings.llm_api_key
model = settings.llm_model
```

### Step 3: Usage Examples

**In embeddings.py**:
```python
if self.provider == "openai":
    openai.api_key = settings.llm_api_key  # Line 17
    client = openai.OpenAI(api_key=settings.llm_api_key)  # Line 48
```

**In vector_store.py**:
```python
self.client = chromadb.PersistentClient(
    path=settings.vector_db_dir,  # Line 22
    settings=ChromaSettings(anonymized_telemetry=False)
)
```

**In endpoints.py**:
```python
if not validate_file_extension(file.filename, settings.allowed_extensions_list):
    raise HTTPException(...)

if not validate_file_size(file_size, settings.max_upload_bytes):
    raise HTTPException(...)
```

## Configuration Validation

### Run Validation Script

```bash
python validate_setup.py
```

This script checks:
- ✅ .env file exists
- ✅ All required variables are set
- ✅ API key is not placeholder
- ✅ Dependencies are installed
- ✅ Config imports work
- ✅ API key is valid (makes test request)

### Manual Validation

```python
# Test config loading
python -c "from backend.app.config import settings; print(settings.llm_provider)"

# Expected output: openai (or gemini)
```

## Troubleshooting

### Issue: "LLM_API_KEY not set"

**Solution**: Create .env file and add your key
```bash
cp .env.example .env
# Edit .env and add: LLM_API_KEY=sk-your-key-here
```

### Issue: "Settings object has no attribute 'llm_api_key'"

**Solution**: Check that environment variable names match exactly:
- In .env: `LLM_API_KEY=...`
- In config.py: `env="LLM_API_KEY"`

### Issue: "Invalid API key"

**Solution**: Verify your key:
1. OpenAI: https://platform.openai.com/api-keys
2. Check it starts with `sk-` (OpenAI) or `AIzaSy` (Gemini)
3. Ensure no extra spaces or quotes

### Issue: "Module not found: pydantic_settings"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Config changes not taking effect

**Solution**: Restart the application
- Settings are loaded once at startup
- After changing .env, restart API and UI

## Security Best Practices

### ✅ DO:
- Keep .env file local (never commit to git)
- Use .env.example as template (without real keys)
- Rotate API keys periodically
- Use environment-specific .env files (.env.prod, .env.dev)

### ❌ DON'T:
- Commit .env to version control
- Share .env file via email/chat
- Hardcode API keys in code
- Use same API key across environments

## Docker Configuration

When using Docker, environment variables can be set in:

### docker-compose.yml
```yaml
services:
  api:
    environment:
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_MODEL=${LLM_MODEL:-gpt-4o-mini}
```

### Docker run command
```bash
docker run \
  -e LLM_PROVIDER=openai \
  -e LLM_API_KEY=sk-your-key \
  -e LLM_MODEL=gpt-4o-mini \
  genai-doc-assistant
```

### Using .env with Docker
```bash
# Docker reads .env automatically
docker-compose up
```

## Production Considerations

### Use Secrets Management

For production, don't use .env files. Use:
- **AWS**: Secrets Manager, Systems Manager Parameter Store
- **Google Cloud**: Secret Manager
- **Azure**: Key Vault
- **Kubernetes**: Secrets
- **HashiCorp**: Vault

### Environment-Specific Configs

```bash
# Development
.env.dev

# Staging
.env.staging

# Production
.env.prod
```

Load with:
```bash
export ENV=prod
# Code: env_file = f".env.{os.getenv('ENV', 'dev')}"
```

## Summary

- ✅ All config in `.env` file
- ✅ Loaded via Pydantic Settings in `config.py`
- ✅ Imported as `settings` in all modules
- ✅ Validated at startup
- ✅ Type-safe with defaults
- ✅ Secure (not in git)

**Key Files**:
1. `.env` - Your config (you create this)
2. `.env.example` - Template (in git)
3. `backend/app/config.py` - Settings class
4. `validate_setup.py` - Validation script

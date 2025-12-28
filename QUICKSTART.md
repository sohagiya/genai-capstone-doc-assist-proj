# QuickStart Guide

Get the GenAI Document Assistant running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- OpenAI API key (or Google Gemini API key)
- 4GB+ RAM

## Step 1: Get an API Key

### OpenAI (Recommended)
1. Go to https://platform.openai.com/api-keys
2. Create account / Login
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Alternative: Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Create account / Login
3. Click "Create API key"
4. Copy the key

## Step 2: Setup Project

### Windows
```cmd
# Run setup script
setup.bat

# It will:
# - Create virtual environment
# - Install dependencies
# - Create .env file
```

### Linux/macOS
```bash
# Make scripts executable
chmod +x setup.sh run_api.sh run_ui.sh

# Run setup
./setup.sh

# It will:
# - Create virtual environment
# - Install dependencies
# - Create .env file
```

## Step 3: Configure API Key

Edit the `.env` file that was created:

```bash
# Open in your editor
notepad .env      # Windows
nano .env         # Linux/macOS
```

Add your API key:

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-actual-key-here
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small
```

For Gemini, use:
```env
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-key-here
LLM_MODEL=gemini-1.5-flash
```

Save and close.

## Step 4: Run the Application

### Option A: Using Scripts (Easiest)

**Windows:**
```cmd
# Terminal 1 - Start API
run_api.bat

# Terminal 2 - Start UI (in a NEW terminal)
run_ui.bat
```

**Linux/macOS:**
```bash
# Terminal 1 - Start API
./run_api.sh

# Terminal 2 - Start UI (in a NEW terminal)
./run_ui.sh
```

### Option B: Manual Run

```bash
# Activate virtual environment
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Terminal 1 - API
python -m uvicorn backend.app.main:app --reload

# Terminal 2 - UI (in NEW terminal, activate venv first)
streamlit run ui/streamlit_app.py
```

### Option C: Docker (No Python Install Needed)

```bash
# Create .env with your API key first!

# Build and run
docker-compose up --build

# Access:
# API: http://localhost:8000
# UI: http://localhost:8501
```

## Step 5: Use the Application

### Access the UI

Open browser: **http://localhost:8501**

### Upload a Document

1. Go to "Upload Documents" tab
2. Click "Choose a file"
3. Select a PDF, TXT, CSV, XLSX, or DOCX file
4. Click "Upload"
5. Wait for "Document uploaded and indexed successfully"

**Try the sample:**
Upload `sample_docs/sample.txt` to get started!

### Ask Questions

1. Go to "Ask Questions" tab
2. Type a question in the text area
3. (Optional) Adjust settings in sidebar:
   - Number of sources (1-10)
   - Answer style (concise/detailed/bullet)
4. Click "Ask"
5. View answer with citations!

### Example Questions (for sample.txt)

- "What is machine learning?"
- "What are the applications of AI?"
- "Explain deep learning"
- "What is NLP?"

## Step 6: Verify Everything Works

### Check API Health

Open browser: **http://localhost:8000/docs**

You should see the Swagger UI with 3 endpoints:
- POST /api/v1/upload-document
- POST /api/v1/ask-question
- GET /api/v1/health-check

Click "GET /health-check" → "Try it out" → "Execute"

Should return:
```json
{
  "status": "healthy",
  "vector_db_connected": true,
  "collection_stats": {
    "collection_name": "documents",
    "total_chunks": 5
  }
}
```

### Run Tests

```bash
# Activate virtual environment first
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Run tests
pytest

# Run with coverage
pytest --cov=backend
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"

**Solution:** Activate virtual environment
```bash
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows
```

### Issue: "Port 8000 already in use"

**Solution:** Kill the process or change port
```bash
# Change port in .env
API_PORT=8001

# Or kill existing process
# Windows: taskkill /F /IM python.exe
# Linux/macOS: pkill -f uvicorn
```

### Issue: "OpenAI API error"

**Solution:** Check your API key
- Make sure it starts with `sk-`
- Verify it's valid at https://platform.openai.com/api-keys
- Check you have credits in your account

### Issue: "Streamlit won't start"

**Solution:**
```bash
# Make sure API is running first
# Check http://localhost:8000/health-check

# Verify UI can connect to API
# Default: http://localhost:8000/api/v1
```

### Issue: Docker "Cannot connect to Docker daemon"

**Solution:**
- Start Docker Desktop (Windows/macOS)
- Or start Docker service (Linux): `sudo systemctl start docker`

## What's Next?

### Try Advanced Features

**Upload Multiple Documents:**
- Upload PDFs, Word docs, Excel files
- Ask questions that span multiple documents
- System will cite sources from each

**Experiment with Settings:**
- Change "answer_style" to "detailed" or "bullet"
- Increase "top_k" for more sources (slower but more comprehensive)
- Try different questions to test the agent pipeline

**View Debug Info:**
- In UI, expand "Debug Information" after each answer
- Check trace_id, reasoning, and citation count
- Use for troubleshooting

### Learn More

Read the documentation in `/docs`:
- [ARCH.md](docs/ARCH.md) - How the system works
- [AGENTS.md](docs/AGENTS.md) - Agent pipeline details
- [API.md](docs/API.md) - API reference
- [SECURITY.md](docs/SECURITY.md) - Security measures

### Develop & Extend

**Add Your Own Documents:**
- Upload company docs, research papers, manuals
- Build a knowledge base for your domain

**Modify the Code:**
- All code is in `backend/app/`
- UI is in `ui/streamlit_app.py`
- Tests are in `tests/`

**Deploy to Production:**
- See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Use Docker for easy deployment
- Consider upgrading ChromaDB to Pinecone for scale

## Directory Structure

```
genai-capstone-doc-assist-proj/
├── backend/app/          # Backend code
│   ├── main.py          # FastAPI entry point
│   ├── api/             # API endpoints
│   ├── core/            # Document processing
│   ├── agents/          # Agent pipeline
│   └── utils/           # Utilities
├── ui/                  # Frontend code
│   └── streamlit_app.py # Streamlit UI
├── tests/               # Test suite
├── docs/                # Documentation
├── sample_docs/         # Example documents
├── .env                 # Your configuration (create from .env.example)
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker setup
└── README.md           # Full documentation
```

## Support

**Need help?**
1. Check [README.md](README.md) for detailed instructions
2. Review [docs/](docs/) for specific topics
3. Check logs for errors (JSON format in terminal)
4. Verify .env configuration
5. Test with sample.txt first

## Success Checklist

- [ ] Python 3.11+ installed
- [ ] API key obtained
- [ ] Dependencies installed (`setup.sh` or `setup.bat`)
- [ ] .env configured with API key
- [ ] API running (http://localhost:8000)
- [ ] UI running (http://localhost:8501)
- [ ] Sample document uploaded
- [ ] Question answered successfully
- [ ] Citations displayed
- [ ] Tests pass

**All checked? You're ready to go! 🚀**

## Quick Command Reference

```bash
# Setup (once)
./setup.sh              # or setup.bat

# Run (every time)
./run_api.sh            # Terminal 1
./run_ui.sh             # Terminal 2

# Test
pytest

# Docker (alternative)
docker-compose up --build

# Stop
Ctrl+C                  # Stop running services
docker-compose down     # Stop Docker services
```

---

**Estimated Time:** 5 minutes to setup, 30 seconds per document upload, instant answers

**Next Steps:** Upload your first document and start asking questions!

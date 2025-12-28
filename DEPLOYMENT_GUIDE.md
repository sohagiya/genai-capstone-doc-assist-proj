# Deployment Guide

## Overview

This guide covers deploying the GenAI Document Assistant for your capstone project demonstration.

## Repository Information

**GitHub Repository:** https://github.com/YOUR_USERNAME/genai-document-assistant

This project is version-controlled with Git and ready for deployment.

---

## Recommended: Local Deployment (Current Setup)

Your application is currently running locally, which is **ideal for capstone demonstrations**.

### Running Services

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Streamlit UI:** http://localhost:8501

### How to Start

**Option 1: Using Shell Scripts**
```bash
# Windows
run_api.bat    # Terminal 1
run_ui.bat     # Terminal 2

# Linux/Mac
./run_api.sh   # Terminal 1
./run_ui.sh    # Terminal 2
```

**Option 2: Manual Commands**
```bash
# Terminal 1 - Start API
cd c:\code\genai-capstone-doc-assist-proj
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start UI
cd c:\code\genai-capstone-doc-assist-proj
streamlit run ui/streamlit_app.py
```

### Benefits of Local Deployment

✅ **Full Feature Access** - All features work perfectly
✅ **No API Key Exposure** - Your OpenAI key stays private
✅ **No Cost** - No cloud hosting fees
✅ **Fast Performance** - No network latency
✅ **Easy Debugging** - Live logs and reload
✅ **Perfect for Demos** - Show professors/reviewers in real-time

---

## GitHub Version Control

Your code is committed to Git and ready to push to GitHub for:
- Version control
- Portfolio showcase
- Collaboration
- Backup

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `genai-document-assistant`
3. Description: `GenAI Document Assistant - RAG-based Q&A System (Capstone Project)`
4. **Keep it Public** (for portfolio) or Private (for academic integrity)
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Push Your Code

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/genai-document-assistant.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: Verify Upload

Visit `https://github.com/YOUR_USERNAME/genai-document-assistant` to see your code.

### What's Included in Git

✅ All source code (51 files)
✅ Documentation (README, guides, architecture docs)
✅ Tests
✅ Docker configuration
✅ Setup scripts
✅ `.env.example` (template with placeholder API key)

### What's NOT in Git (Secure)

❌ `.env` - Your actual API key (protected by `.gitignore`)
❌ `data/` - Vector database files
❌ `temp_uploads/` - Temporary files
❌ `__pycache__/` - Python cache
❌ `.venv/` - Virtual environment

---

## Docker Deployment (Optional)

For containerized deployment on any platform.

### Prerequisites

- Docker installed (✅ Already installed on your system)
- Docker Compose installed (✅ Already installed)

### Quick Start

```bash
# Build and run both API and UI
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Services

After starting with Docker Compose:
- API: http://localhost:8000
- UI: http://localhost:8501

### Configuration

Environment variables are set in `docker-compose.yml`. Update them before deploying:

```yaml
services:
  api:
    environment:
      - LLM_PROVIDER=openai
      - LLM_API_KEY=${LLM_API_KEY}  # Reads from .env file
      - LLM_MODEL=gpt-4o-mini
      # ... other vars
```

---

## Cloud Deployment (Advanced)

### Important Limitations

⚠️ **Streamlit Community Cloud** does NOT support this architecture because:
- It only deploys Streamlit apps (no FastAPI backend)
- Our app requires both API + UI running simultaneously
- Would need significant architectural changes

### Alternative Cloud Platforms

If you need cloud deployment, consider these platforms:

#### 1. **Railway** (Easiest)
- Free tier available
- Supports multi-service deployments
- Auto-detects Python apps
- Easy GitHub integration

**Steps:**
1. Push code to GitHub (see above)
2. Go to https://railway.app/
3. "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in Railway dashboard
6. Deploy both `backend` and `ui` as separate services

#### 2. **Render** (Good Free Tier)
- Free web services
- Supports Docker
- PostgreSQL included

**Steps:**
1. Push code to GitHub
2. Go to https://render.com/
3. "New" → "Web Service"
4. Connect GitHub repository
5. Deploy as Docker container using `docker-compose.yml`

#### 3. **Heroku** (Classic Platform)
- Easy deployment
- Requires `Procfile` configuration
- Free tier available (with limitations)

#### 4. **AWS/GCP/Azure** (Enterprise)
- Most flexible
- Use EC2/Compute Engine/VM with Docker
- Requires more DevOps knowledge

---

## Production Considerations

### Security

For production deployment:

1. **API Key Management**
   - Use cloud secrets manager (AWS Secrets Manager, GCP Secret Manager)
   - Never commit `.env` to Git (✅ already protected)
   - Rotate keys regularly

2. **Authentication**
   - Add user authentication to the API
   - Implement rate limiting
   - Use HTTPS/SSL certificates

3. **Database**
   - Use persistent storage for ChromaDB
   - Regular backups
   - Consider cloud vector DB (Pinecone, Weaviate)

### Monitoring

- Add application monitoring (Sentry, DataDog)
- Track API usage and costs
- Monitor LLM token consumption

### Scaling

- Use Redis for caching
- Load balancer for multiple API instances
- CDN for static assets

---

## Troubleshooting

### Issue: Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: Git Push Rejected

**Error:** `Updates were rejected because the remote contains work`

**Solution:**
```bash
# Force push (first time only)
git push -u origin main --force
```

### Issue: Docker Container Won't Start

**Solution:**
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down
docker-compose up --build
```

### Issue: API Key Not Working

**Solution:**
1. Check `.env` file exists in project root
2. Verify API key starts with `sk-proj-` (OpenAI)
3. Test with validation script:
   ```bash
   python validate_setup.py
   ```

---

## Recommended Workflow for Capstone Demo

### Before Demonstration

1. ✅ Ensure both API and UI are running locally
2. ✅ Test document upload with sample files
3. ✅ Verify Q&A functionality works
4. ✅ Clear old documents if needed
5. ✅ Check API health: http://localhost:8000/api/v1/health-check

### During Demonstration

1. **Show Architecture**
   - Explain multi-agent pipeline
   - Show API documentation at `/docs`
   - Demonstrate document management

2. **Live Demo**
   - Upload a relevant document
   - Ask meaningful questions
   - Show citation sources
   - Demonstrate document deletion/clearing

3. **Show Code Quality**
   - GitHub repository structure
   - Documentation completeness
   - Test coverage
   - Docker deployment setup

### After Demonstration

1. Push final version to GitHub
2. Create a release/tag for submission
3. Include GitHub URL in capstone report

---

## Deployment Checklist

### Local Deployment (Recommended)
- [x] Git repository initialized
- [ ] Code pushed to GitHub
- [x] API running on port 8000
- [x] UI running on port 8501
- [x] `.env` configured with valid API key
- [x] Sample documents ready for demo

### Docker Deployment (Optional)
- [x] Docker installed
- [x] Docker Compose installed
- [ ] `docker-compose.yml` configured
- [ ] Environment variables set
- [ ] Successfully built and run

### Cloud Deployment (Advanced)
- [ ] Cloud platform selected
- [ ] Repository connected
- [ ] Environment secrets configured
- [ ] Services deployed and tested
- [ ] Custom domain configured (optional)

---

## Summary

**For Capstone Project Demonstration:**

✅ **Best Choice: Local Deployment**
- Already working perfectly
- Full features available
- No additional setup needed
- Ideal for live demos

✅ **Recommended: Push to GitHub**
- Version control
- Portfolio showcase
- Easy sharing with professors

❌ **Not Recommended: Cloud Deployment**
- Adds complexity
- Potential costs
- Not necessary for capstone demo
- May have feature limitations

---

## Need Help?

- Check API logs in Terminal 1
- Check UI logs in Terminal 2
- Run validation: `python validate_setup.py`
- Check API health: http://localhost:8000/api/v1/health-check
- Review documentation in `/docs` folder

---

**Your app is production-ready for local demonstration!** 🚀

The current local setup is perfect for your capstone project. GitHub integration provides version control and portfolio value without the complexity of cloud deployment.

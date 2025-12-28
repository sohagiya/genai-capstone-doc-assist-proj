# Deployment Documentation

## Overview

This document provides instructions for deploying the GenAI Document Assistant in various environments.

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.11 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk**: 2GB free space (more for document storage)
- **Network**: Internet connection for LLM API calls

### Required Credentials

- OpenAI API key OR Google Gemini API key
- (Obtain from respective provider websites)

## Local Deployment

### Option 1: Direct Python Run

**Step 1: Clone Repository**

```bash
git clone <repository-url>
cd genai-capstone-doc-assist-proj
```

**Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

**Step 3: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4: Configure Environment**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your API key
# Windows: notepad .env
# Linux/macOS: nano .env
```

Required settings in `.env`:
```
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-actual-api-key-here
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small
```

**Step 5: Run the API Server**

```bash
# Development mode (with auto-reload)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode (without reload)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

**Step 6: Run the UI (separate terminal)**

```bash
# Activate venv first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run Streamlit
streamlit run ui/streamlit_app.py
```

UI will be available at: `http://localhost:8501`

**Step 7: Verify Deployment**

```bash
# Check API health
curl http://localhost:8000/api/v1/health-check

# Open browser
# API docs: http://localhost:8000/docs
# UI: http://localhost:8501
```

### Option 2: Docker Compose (Recommended)

**Step 1: Clone Repository**

```bash
git clone <repository-url>
cd genai-capstone-doc-assist-proj
```

**Step 2: Configure Environment**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API key
```

**Step 3: Build and Run**

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build
```

**Services Started:**
- API: `http://localhost:8000`
- UI: `http://localhost:8501`

**Step 4: Verify**

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f

# Check API health
curl http://localhost:8000/api/v1/health-check
```

**Step 5: Stop Services**

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears data)
docker-compose down -v
```

## Docker Deployment Details

### Single Container (API Only)

```bash
# Build image
docker build -t genai-doc-assistant .

# Run container
docker run -d \
  -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e LLM_API_KEY=your-api-key \
  -e LLM_MODEL=gpt-4o-mini \
  -e EMBEDDINGS_MODEL=text-embedding-3-small \
  -v $(pwd)/data:/app/data \
  --name genai-api \
  genai-doc-assistant
```

### Multi-Container (docker-compose)

```yaml
# docker-compose.yml structure:
services:
  api:    # FastAPI backend on port 8000
  ui:     # Streamlit frontend on port 8501
volumes:
  chroma_data:  # Persistent vector database
```

**Volume Persistence:**
- Vector database persists across restarts
- Uploaded documents indexed once
- To reset: `docker-compose down -v`

## Production Deployment

### Recommended Setup

```
┌─────────────┐
│ Load        │
│ Balancer    │ (Nginx/HAProxy)
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌─────┐ ┌─────┐
│ API │ │ API │  (Multiple instances)
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       ▼
┌─────────────┐
│ Vector DB   │  (Shared or replicated)
└─────────────┘
```

### Environment Configuration

**Production `.env`:**

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=sk-prod-key-here  # Use secrets management!
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small

# Vector DB (use absolute path or network storage)
VECTOR_DB_DIR=/var/lib/genai/chroma

# Upload limits
MAX_UPLOAD_MB=10

# API config
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Secrets Management

**DO NOT** commit `.env` with real API keys!

**Options:**

1. **Environment Variables (Docker)**
   ```bash
   docker run -e LLM_API_KEY=$(cat /secrets/llm_key) ...
   ```

2. **Docker Secrets**
   ```bash
   echo "sk-your-key" | docker secret create llm_api_key -
   ```

3. **External Secrets Manager**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

4. **Kubernetes Secrets**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: llm-api-key
   data:
     key: <base64-encoded-key>
   ```

### Reverse Proxy (Nginx)

**nginx.conf example:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # UI
    location / {
        proxy_pass http://localhost:8501/;
        proxy_set_header Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**HTTPS with Let's Encrypt:**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com
```

### Process Management (Systemd)

**API Service** (`/etc/systemd/system/genai-api.service`):

```ini
[Unit]
Description=GenAI Document Assistant API
After=network.target

[Service]
User=genai
WorkingDirectory=/opt/genai-doc-assistant
Environment="PATH=/opt/genai-doc-assistant/venv/bin"
EnvironmentFile=/opt/genai-doc-assistant/.env
ExecStart=/opt/genai-doc-assistant/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**

```bash
sudo systemctl enable genai-api
sudo systemctl start genai-api
sudo systemctl status genai-api
```

## Cloud Deployment

### AWS (Example)

**Option 1: EC2 + Docker**

```bash
# Launch EC2 instance (t3.medium or larger)
# SSH into instance
ssh -i key.pem ubuntu@ec2-instance

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Clone repo
git clone <repo-url>
cd genai-doc-assistant

# Set environment
echo "LLM_API_KEY=your-key" > .env

# Run
sudo docker-compose up -d
```

**Option 2: ECS (Fargate)**

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Create ECS service
4. Configure load balancer

**Option 3: Lambda (API only, cold start considerations)**

### Google Cloud Platform

**Cloud Run** (recommended for containerized apps):

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/genai-doc-assistant

# Deploy
gcloud run deploy genai-api \
  --image gcr.io/PROJECT_ID/genai-doc-assistant \
  --platform managed \
  --region us-central1 \
  --set-env-vars LLM_PROVIDER=openai,LLM_API_KEY=your-key
```

### Azure

**Azure Container Instances**:

```bash
az container create \
  --resource-group myResourceGroup \
  --name genai-doc-assistant \
  --image genai-doc-assistant:latest \
  --dns-name-label genai-app \
  --ports 8000 8501 \
  --environment-variables LLM_API_KEY=your-key
```

## Scaling Considerations

### Horizontal Scaling

**API Instances:**
- Run multiple API containers
- Use load balancer
- Share vector database (use network storage)

**Limitations:**
- ChromaDB not designed for multi-writer
- Consider upgrading to Pinecone/Weaviate for production

### Vertical Scaling

- Increase container memory
- More CPU for faster embedding generation
- SSD for better vector DB performance

### Database Scaling

**ChromaDB (current):**
- Single-node, file-based
- Good for POC, not production scale

**Production Options:**
- **Pinecone**: Managed, scalable vector DB
- **Weaviate**: Self-hosted, distributed
- **Milvus**: Open-source, production-ready
- **FAISS**: Facebook's library (in-memory)

**Migration Path:**

Code is abstracted via `VectorStore` class - swap backend:

```python
# In vector_store.py
class VectorStore:
    def __init__(self):
        if settings.vector_db_backend == "pinecone":
            self.client = PineconeClient(...)
        elif settings.vector_db_backend == "chroma":
            self.client = chromadb.Client(...)
```

## Monitoring

### Health Checks

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /api/v1/health-check
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
```

### Logging

**Centralized Logging:**

```bash
# Docker logs to CloudWatch (AWS)
--log-driver=awslogs

# Aggregate logs with ELK Stack
docker-compose logs | logstash
```

**JSON Logs:**

All logs are JSON-formatted for easy parsing:

```json
{"timestamp": "2024-01-15T10:30:00", "level": "INFO", "message": "Question processed", "trace_id": "abc123"}
```

### Metrics

**Recommended Metrics:**

- Request count
- Response latency (p50, p95, p99)
- Error rate
- LLM API latency
- Vector search latency
- Document upload count
- Active documents/chunks

**Tools:**
- Prometheus + Grafana
- AWS CloudWatch
- Google Cloud Monitoring
- Datadog

## Backup and Recovery

### Vector Database Backup

```bash
# Backup ChromaDB
tar -czf chroma-backup-$(date +%Y%m%d).tar.gz data/chroma/

# Restore
tar -xzf chroma-backup-20240115.tar.gz
```

### Automated Backups

```bash
# Cron job (daily at 2 AM)
0 2 * * * cd /opt/genai && tar -czf /backups/chroma-$(date +\%Y\%m\%d).tar.gz data/chroma/
```

## Troubleshooting

### Common Issues

**Issue:** API won't start

```bash
# Check logs
docker-compose logs api

# Common causes:
- LLM_API_KEY not set
- Port 8000 already in use
- Python dependencies missing
```

**Issue:** Vector DB connection failed

```bash
# Check directory permissions
ls -la data/chroma/

# Create directory if missing
mkdir -p data/chroma
```

**Issue:** Out of memory

```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory

# Or limit in docker-compose:
services:
  api:
    mem_limit: 2g
```

**Issue:** Slow response times

```bash
# Check LLM API latency
# Check vector DB size (too many chunks)
# Consider caching frequent queries
```

## Security Hardening

### Production Checklist

- [ ] Use HTTPS only (TLS 1.2+)
- [ ] Store API keys in secrets manager
- [ ] Restrict CORS to specific domains
- [ ] Add rate limiting
- [ ] Enable request logging
- [ ] Use non-root user in Docker
- [ ] Scan Docker images for vulnerabilities
- [ ] Implement authentication
- [ ] Add firewall rules
- [ ] Regular security updates

### Docker Security

```dockerfile
# Use non-root user
RUN useradd -m -u 1000 genai
USER genai

# Read-only filesystem
docker run --read-only ...

# Drop capabilities
docker run --cap-drop=ALL ...
```

## Cost Optimization

### LLM API Costs

- Use smaller models where possible (gpt-4o-mini vs gpt-4)
- Cache frequent questions
- Limit max_tokens in responses
- Monitor usage via provider dashboard

### Infrastructure Costs

- Use auto-scaling (scale to zero when idle)
- Spot instances for non-critical workloads
- Right-size containers (don't over-provision)
- Use CDN for UI assets

## Maintenance

### Regular Tasks

- **Daily**: Check logs for errors
- **Weekly**: Review API usage and costs
- **Monthly**: Update dependencies (`pip list --outdated`)
- **Quarterly**: Security audit

### Updates

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Rebuild Docker image
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

## Support

For deployment issues:
1. Check logs first
2. Review health check endpoint
3. Verify environment variables
4. Check GitHub issues
5. Contact support team

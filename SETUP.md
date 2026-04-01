# Complete Setup & Running Guide

## Project Structure

```
pdfdec/
├── backend/
│   ├── main.py                 # FastAPI + Celery backend
│   ├── pdf_parser.py           # PDF parsing logic
│   ├── graph_builder.py        # Neo4j integration
│   ├── vector_store.py         # Qdrant integration
│   ├── .venv/                  # Python virtual environment
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   └── DocumentViewer.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── README.md
└── README.md
```

## Prerequisites

### System Requirements
- Windows/Mac/Linux
- Python 3.9+
- Node.js 16+
- Docker (optional, for running databases)

### Required Services
1. **Neo4j** - Graph Database
2. **Qdrant** - Vector Database
3. **Redis** - Message Broker for Celery
4. **Fastapi** - Web Framework
5. **Celery** - Background Task Queue

## Step-by-Step Setup

### 1. Backend Setup

#### A. Start Databases

**Option 1: Docker (Recommended)**
```bash
# Neo4j
docker run -d \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Qdrant
docker run -d \
  -p 6333:6333 \
  qdrant/qdrant:latest

# Redis
docker run -d \
  -p 6379:6379 \
  redis:alpine
```

**Option 2: Manual Installation**
- Download and install from official websites:
  - Neo4j: https://neo4j.com/download/
  - Qdrant: https://qdrant.tech/documentation/quick-start/
  - Redis: https://redis.io/download/

#### B. Install Python Dependencies

```bash
cd pdfdec
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```
fastapi==0.104.0
uvicorn==0.24.0
celery==5.3.0
redis==5.0.0
neo4j==5.13.0
qdrant-client==2.7.0
sentence-transformers==2.2.2
pydantic==2.5.0
python-multipart==0.0.6
pdfplumber==0.10.0
pillow==10.1.0
requests==2.31.0
```

#### C. Update Database Credentials (if different)

Edit these files if your database credentials differ:
- `main.py`: Line with Neo4j connection
- `pdf_parser.py`: Any database references
- `graph_builder.py`: Neo4j credentials

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
cp .env.example .env
# Edit .env if your backend is on different host/port
```

---

## Running the Application

### Terminal 1: Backend API Server

```bash
cd pdfdec
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

python main.py
# API will be available at http://localhost:8000
```

### Terminal 2: Celery Worker

```bash
cd pdfdec
source .venv/bin/activate

celery -A main.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Frontend Development Server

```bash
cd pdfdec/frontend

npm run dev
# Frontend will be available at http://localhost:3000
```

---

## Verifying Setup

### 1. Check Backend

```bash
# Should return API documentation
curl http://localhost:8000/docs
```

### 2. Check Databases

**Neo4j:**
- Visit: http://localhost:7474
- Default credentials: neo4j / password

**Qdrant:**
```bash
curl http://localhost:6333/
```

**Redis:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Test Upload

```bash
# Have a sample.pdf ready
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@sample.pdf"

# Should return something like:
# {
#   "message": "Document accepted for processing",
#   "book_id": "doc_9d4a54da",
#   "task_id": "abc123..."
# }
```

---

## Workflow

1. **Open Frontend** → http://localhost:3000
2. **Upload PDF** → Click upload, select PDF file
3. **Wait for Processing** → See progress bar (10-30 seconds)
4. **View Document** → Switch to "View Documents" tab
5. **Search** → Use search box to find relevant content

---

## Build for Production

### Frontend

```bash
cd frontend

npm run build
# Output in: frontend/dist/

# Deploy dist/ folder to your web server
```

### Backend

Create a production configuration:
```python
# config/prod.py
class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@host/db"
    CELERY_BROKER_URL = "redis://celery-broker:6379/0"
    CELERY_RESULT_BACKEND = "redis://celery-backend:6379/1"
```

Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000                    # Mac/Linux
netstat -ano | findstr :8000    # Windows

# Kill process
kill -9 <PID>
```

### Database Connection Error

```python
# Test connection
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
driver.verify_connectivity()
```

### Celery Worker Not Processing

Check Redis is running:
```bash
redis-cli PING
# Should return: PONG

# Check Celery tasks
redis-cli
> KEYS *
```

### Vector Database Empty

Check Qdrant collections:
```bash
curl http://localhost:6333/collections
```

### Frontend 404 on API Calls

1. Verify backend is running on port 8000
2. Check VITE_API_BASE_URL in .env
3. Check CORS is enabled in main.py

---

## Development Tips

### Enable Debug Mode

```python
# In main.py
app = FastAPI(debug=True)
```

### Monitor Celery Tasks

```bash
# In separate terminal
celery -A main.celery_app inspect active
celery -A main.celery_app inspect stats
```

### Frontend Hot Reload

Already enabled by default with Vite:
```bash
npm run dev
```

### Database Cleanup

```bash
# Neo4j - Delete all data
MATCH (n) DETACH DELETE n

# Qdrant - Delete collection
DELETE /collections/document_chunks
```

---

## Performance Optimization

### For Large Documents
- Increase Celery worker processes
- Enable Redis persistence
- Optimize PDF parser batch sizes

### For Many Users
- Set up load balancer (Nginx)
- Use connection pooling
- Cache frequent searches

### Vector Search Tuning
- Adjust HNSW parameters in Qdrant
- Experiment with embedding models
- Use filters to reduce search space

---

## Next Steps

After successful setup:

1. ✅ Upload sample PDFs
2. ✅ Test search functionality
3. ✅ Customize frontend styling
4. ✅ Add authentication (JWT)
5. ✅ Deploy to production
6. ✅ Set up monitoring/logging
7. ✅ Add batch processing API

---

## Support & Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Neo4j Docs:** https://neo4j.com/docs/
- **Qdrant Docs:** https://qdrant.tech/documentation/
- **React Docs:** https://react.dev/
- **Celery Docs:** https://docs.celeryproject.io/

---

## License

[Your License Here]

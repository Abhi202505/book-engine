# Quick Start Guide

Get the PDF Document Intelligence system up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose (easiest way)
- OR: Python 3.9+, Node.js 16+, and Docker for databases

## Option 1: Docker Compose (Recommended)

### 1. Start Everything

```bash
docker-compose up -d
```

Wait for all services to be ready (check with `docker-compose logs -f`).

### 2. Access the Application

Open your browser:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Neo4j Dashboard:** http://localhost:7474 (neo4j / password)
- **Qdrant UI:** http://localhost:6333/dashboard

### 3. Upload Your First Document

1. Go to http://localhost:3000
2. Click "📤 Upload Document"
3. Select a PDF file
4. Click "🚀 Upload & Process"
5. Wait for processing to complete
6. Switch to "📖 View Documents" tab to see results

### 4. Search Documents

1. Select your document from the dropdown
2. Enter a search query (e.g., "machine learning")
3. Click "Search"
4. View results with relevance scores

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f frontend
```

---

## Option 2: Manual Setup (Windows/Mac/Linux)

### Step 1: Install & Start Databases

#### Using Docker (minimum requirement)

```bash
# Neo4j
docker run -d -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Qdrant
docker run -d -p 6333:6333 \
  qdrant/qdrant:latest

# Redis
docker run -d -p 6379:6379 \
  redis:alpine
```

### Step 2: Backend Setup

```bash
# Navigate to project
cd pdfdec

# Create virtual environment
python -m venv .venv

# Activate (choose your OS)
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
# In new terminal/tab
cd frontend
npm install
```

### Step 4: Run Services

**Terminal 1 - Backend API:**
```bash
cd pdfdec
source .venv/bin/activate  # or .venv\Scripts\activate
python main.py
```

**Terminal 2 - Celery Worker:**
```bash
cd pdfdec
source .venv/bin/activate  # or .venv\Scripts\activate
celery -A main.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Access Application

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## Testing the Setup

### Test Backend

```bash
# Check if API is running
curl http://localhost:8000/docs

# Check Celery (should return PONG)
redis-cli PING
```

### Test Upload

```bash
# Have a test.pdf file ready
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@test.pdf"

# Copy the task_id and check status
curl http://localhost:8000/api/v1/task/{task_id}
```

### View Data in Databases

**Neo4j:**
1. Go to http://localhost:7474
2. Login: neo4j / password
3. Run query: `MATCH (p:Paragraph) RETURN COUNT(p) as paragraphs`

**Qdrant:**
```bash
curl http://localhost:6333/collections
```

---

## Common Issues & Fixes

### Port Already in Use

```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

### Database Connection Failed

```bash
# Check if containers are running
docker ps

# Check logs
docker logs pdfdec-neo4j
docker logs pdfdec-redis
docker logs pdfdec-qdrant
```

### Frontend Won't Connect to API

1. Verify backend is running: `http://localhost:8000/docs`
2. Check frontend `.env` file has correct `VITE_API_BASE_URL`
3. Check browser console for CORS errors

### Celery Worker Not Processing

1. Check Redis is running: `redis-cli PING` should return "PONG"
2. Verify task is queued: `redis-cli`
3. Check worker logs for errors

---

## Next Steps

1. ✅ Upload multiple PDF documents
2. ✅ Test search functionality
3. ✅ Explore Neo4j graph structure
4. ✅ Review API documentation at http://localhost:8000/docs
5. ✅ Read [SETUP.md](./SETUP.md) for detailed configuration
6. ✅ Check [API_REFERENCE.md](./API_REFERENCE.md) for endpoints

---

## Useful Commands

```bash
# Stop all services
docker-compose down

# Stop & remove volumes (full cleanup)
docker-compose down -v

# View backend logs
docker-compose logs -f backend

# View celery worker logs
docker-compose logs -f celery-worker

# View frontend logs
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Run a command in a container
docker-compose exec backend bash

# Check database health
docker-compose exec redis redis-cli PING
docker-compose exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

---

## Performance Tips

- For faster uploads: Use PDF files under 50MB
- For better search: Use 5-10 word queries
- For multiple documents: Wait for each to finish before uploading next
- Monitor Celery tasks in Redis dashboard

---

## Need Help?

- Check Docker logs: `docker-compose logs`
- Read detailed setup: [SETUP.md](./SETUP.md)
- API documentation: http://localhost:8000/docs
- Frontend issues: Check browser console (F12)

---

**That's it! You're ready to use PDF Document Intelligence! 🚀**

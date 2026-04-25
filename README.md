# PDF Document Intelligence System

A full-stack application for uploading, parsing, embedding, and searching PDF documents using Neo4j, Qdrant, and machine learning.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Node.js](https://img.shields.io/badge/Node.js-16+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

##  Features

- ** Document Upload** - Upload PDF files through intuitive web interface
- ** PDF Parsing** - Advanced layout analysis and text extraction
- ** Embeddings** - Convert text to semantic vectors for intelligent search
- ** Graph Storage** - Structure documents as knowledge graphs in Neo4j
- ** Vector Search** - Semantic search using Qdrant vector database
- ** Async Processing** - Background task processing with Celery
- ** Modern UI** - React + Vite frontend with real-time processing updates
- ** Responsive Design** - Works on desktop and mobile devices



##  Quick Start

### 1. Clone & Setup

```bash
git clone <repo>
cd pdfdec

# Backend setup
cd pdfdec
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Start Services

```bash
# Terminal 1: FastAPI Backend
cd pdfdec
source .venv/bin/activate
python main.py

# Terminal 2: Celery Worker
cd pdfdec
source .venv/bin/activate
python celery_worker.py

# Terminal 3: Frontend
cd frontend
npm run dev
```

### 3. Access Application

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Neo4j:** http://localhost:7474
- **Qdrant:** http://localhost:6333

##  Documentation

- **[Setup Guide](./SETUP.md)** - Detailed installation and configuration
- **[API Reference](./API_REFERENCE.md)** - Backend API documentation
- **[Frontend README](./frontend/README.md)** - Frontend development guide

## Tech Stack

### Backend
- **FastAPI** - Web framework
- **Celery** - Task queue
- **Neo4j** - Graph database
- **Qdrant** - Vector database
- **Redis** - Message broker
- **SentenceTransformers** - Embeddings

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS3** - Styling

##  API Endpoints

### Document Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload PDF file |
| GET | `/api/v1/task/{task_id}` | Get processing status |
| GET | `/api/v1/documents/{book_id}` | Get document paragraphs |
| GET | `/api/v1/documents/{book_id}/search` | Search document |

See [API Reference](./API_REFERENCE.md) for detailed endpoint documentation.

##  Workflow

```
1. User uploads PDF
   ↓
2. Backend queues processing task
   ↓
3. Celery worker processes PDF
   ├─ Extracts text & layout
   ├─ Generates embeddings
   ├─ Stores in Neo4j
   └─ Indexes in Qdrant
   ↓
4. Frontend polls task status
   ↓
5. Document ready for search & viewing
```

##  Database Schema

### Neo4j Graph
```
Book
├── Section
│   ├── Paragraph [HAS_TEXT]
│   │   └── Image [HAS_IMAGE]
│   └── Paragraph → NEXT → Paragraph
```

### Qdrant Collections
```
document_chunks
├── Vector (768-dim semantic embedding)
├── Text (paragraph content)
├── Page Number
└── Book ID
```

##  Frontend Features

-  Drag-and-drop file upload
-  Real-time processing progress
-  Document visualization in grid layout
-  Semantic search with relevance scoring
-  Pagination and filtering
-  Metadata display
-  Responsive mobile design

##  Security Considerations

For production deployment:
- [ ] Enable authentication (JWT)
- [ ] Add rate limiting
- [ ] Validate file uploads
- [ ] Encrypt sensitive data
- [ ] Use HTTPS
- [ ] Set CORS correctly
- [ ] Add request logging
- [ ] Implement access control

##  Troubleshooting

### Backend Won't Start
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :6379

# Check Python environment
which python
python --version
```

### Database Connection Failed
```bash
# Check service status
docker ps | grep neo4j
docker ps | grep qdrant
docker ps | grep redis
```

### Frontend Won't Load
```bash
# Check API connectivity
curl http://localhost:8000/docs

# Check CORS settings
# Verify frontend port matches CORS allowlist
```

See [SETUP.md](./SETUP.md#troubleshooting) for more solutions.

##  Performance Tips

- Use batch uploads for multiple files
- Optimize embeddings model for your use case
- Enable Redis persistence
- Configure Celery worker pool size
- Use CDN for frontend assets in production
- Set up database indexing on frequently searched fields

##  Deployment

### Docker Compose (Recommended)
```bash
docker-compose up -d
# Brings up all services

docker-compose down
# Stop all services
```

### Cloud Platforms
- **AWS:** EC2 + RDS (Neo4j) + S3
- **Azure:** App Service + Cosmos DB + Blob Storage
- **GCP:** Run on Cloud Run + Firestore + Cloud Storage

### Scaling Strategies
- Horizontal scaling: Multiple Celery workers
- Database sharding: By book_id
- Caching: Redis cache for frequent searches
- Load balancing: Nginx/HAProxy

##  License

MIT License - See LICENSE file for details

##  Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

##  Support

For issues, questions, or suggestions:
- Open an [Issue](../issues)
- Submit a [Pull Request](../pulls)
- Contact: [your-email@example.com]

##  Roadmap

- [ ] Multi-language support
- [ ] Advanced OCR for scanned PDFs
- [ ] Document comparison tool
- [ ] Export/share functionality
- [ ] Advanced caching layer
- [ ] Real-time collaboration
- [ ] Mobile app (React Native)
- [ ] Batch processing API

##  Related Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Documentation](https://react.dev/)
- [Celery User Guide](https://docs.celeryproject.io/)

---


Last Updated: March 2026

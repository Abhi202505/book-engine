# Project Index & Documentation Guide

## 📑 Document Overview

This file provides a guide to all documentation and files in the PDF Document Intelligence project.

---

## 🚀 Getting Started

**Start here:** [QUICKSTART.md](./QUICKSTART.md)
- 5-minute setup using Docker Compose
- Manual setup instructions
- Common troubleshooting

---

## 📚 Main Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](./README.md) | Project overview, features, architecture | 10 min |
| [QUICKSTART.md](./QUICKSTART.md) | Quick setup guide | 5 min |
| [SETUP.md](./SETUP.md) | Detailed installation & configuration | 20 min |
| [API_REFERENCE.md](./API_REFERENCE.md) | Backend API endpoints | 15 min |
| [frontend/README.md](./frontend/README.md) | Frontend development guide | 10 min |

---

## 🗂️ Project Structure

```
pdfdec/
├── 📄 Main Files
│   ├── main.py                 # FastAPI backend + Celery tasks
│   ├── pdf_parser.py           # PDF parsing logic
│   ├── graph_builder.py        # Neo4j integration
│   ├── vector_store.py         # Qdrant integration
│   └── requirements.txt        # Python dependencies
│
├── 📚 Documentation
│   ├── README.md               # Project overview
│   ├── QUICKSTART.md           # Quick setup guide
│   ├── SETUP.md                # Detailed setup
│   ├── API_REFERENCE.md        # API documentation
│   └── INDEX.md                # This file
│
├── 🐳 Docker Files
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── Dockerfile.backend      # Backend container
│   └── frontend/Dockerfile     # Frontend container
│
├── 🌐 Frontend
│   ├── src/
│   │   ├── App.jsx             # Main app component
│   │   ├── main.jsx            # React entry point
│   │   ├── api/
│   │   │   └── client.js       # API integration
│   │   ├── components/
│   │   │   ├── FileUpload.jsx  # Upload UI
│   │   │   └── DocumentViewer.jsx # View/search UI
│   │   └── styles/             # CSS files
│   ├── package.json            # NPM dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── README.md               # Frontend guide
│   └── Dockerfile              # Frontend container
│
├── ⚙️ Configuration
│   ├── .env.example            # Environment variables template
│   └── .gitignore              # Git ignore rules
│
└── 📦 Dependencies
    ├── requirements.txt        # Python packages
    └── frontend/package.json   # NPM packages
```

---

## 🔧 Configuration Files

### Backend Configuration

**Environment Variables** (`.env`)
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

See [.env.example](./.env.example) for all variables.

### Frontend Configuration

**Environment Variables** (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

See [frontend/.env.example](./frontend/.env.example) for details.

---

## 🏗️ System Architecture

### Services & Ports

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI Backend | 8000 | REST API server |
| React Frontend | 3000 | Web UI |
| Neo4j HTTP | 7474 | Database dashboard |
| Neo4j Bolt | 7687 | Database driver |
| Qdrant | 6333 | Vector database |
| Redis | 6379 | Message broker |

### Data Flow

```
1. Frontend (React)
   ↓ [HTTP POST] Upload PDF
   ↓
2. Backend (FastAPI)
   ├─→ Queue task to Celery
   └─→ Return task_id
   ↓
3. Celery Worker
   ├─→ Parse PDF (pdf_parser.py)
   ├─→ Store to Neo4j (graph_builder.py)
   └─→ Index in Qdrant (vector_store.py)
   ↓
4. Frontend [polls]
   ↓ [HTTP GET] Task status
   ↓
5. Backend returns status
   ↓
6. Frontend displays results
```

---

## 🔑 Key Components

### Backend Services

**main.py** - FastAPI application
- `POST /api/v1/upload` - Upload PDF
- `GET /api/v1/task/{task_id}` - Check task status
- `GET /api/v1/documents/{book_id}` - Get paragraphs
- `GET /api/v1/documents/{book_id}/search` - Search

**pdf_parser.py** - PDF parsing
- Extracts text and layout
- Detects sections and paragraphs
- Identifies images and links

**graph_builder.py** - Neo4j integration
- Creates graph structure
- Manages relationships
- Queries paragraphs

**vector_store.py** - Qdrant integration
- Generates embeddings
- Stores vectors
- Performs semantic search

### Frontend Components

**App.jsx** - Main component
- Tab navigation
- State management

**FileUpload.jsx** - Upload interface
- Drag-and-drop upload
- Progress tracking
- Status polling

**DocumentViewer.jsx** - Document display
- Paragraph grid
- Search interface
- Result highlighting

---

## 📖 API Quick Reference

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.pdf"
```

Response:
```json
{
  "message": "Document accepted for processing",
  "book_id": "doc_9d4a54da",
  "task_id": "abc123..."
}
```

### Check Status
```bash
curl http://localhost:8000/api/v1/task/abc123
```

### Get Document
```bash
curl http://localhost:8000/api/v1/documents/doc_9d4a54da
```

### Search
```bash
curl "http://localhost:8000/api/v1/documents/doc_9d4a54da/search?q=machine+learning"
```

See [API_REFERENCE.md](./API_REFERENCE.md) for complete details.

---

## 🐛 Debugging Guide

### Check Backend Status
```bash
# API health check
curl http://localhost:8000/docs

# Worker status
celery -A main.celery_app inspect active

# Database connection
docker exec pdfdec-neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Database Debugging

**Neo4j (http://localhost:7474)**
```cypher
# Count all paragraphs
MATCH (p:Paragraph) RETURN COUNT(p)

# Find paragraphs by book
MATCH (p:Paragraph {book_id: 'doc_9d4a54da'}) RETURN p LIMIT 10

# View graph structure
MATCH (p:Paragraph)-[r]->(q) RETURN TYPE(r), COUNT(*) GROUP BY TYPE(r)
```

**Qdrant (http://localhost:6333)**
```bash
# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/document_chunks
```

---

## 📦 Dependencies

### Backend (Python)

**Core Framework**
- fastapi - Web framework
- uvicorn - ASGI server
- celery - Task queue
- redis - Message broker

**Databases**
- neo4j - Graph database
- qdrant-client - Vector store

**ML/NLP**
- sentence-transformers - Embeddings
- transformers - NLP models
- torch - Deep learning

**Processing**
- pdfplumber - PDF parsing
- pillow - Image processing
- pydantic - Data validation

### Frontend (JavaScript)

**Core**
- react - UI framework
- react-dom - React DOM
- axios - HTTP client

**Build**
- vite - Build tool
- @vitejs/plugin-react - React plugin

---

## 🚀 Deployment

### Development
```bash
docker-compose up -d
# Services run in background with auto-reload
```

### Production
```bash
# Build images
docker-compose build

# Run detached
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose up -d --scale celery-worker=3
```

See [SETUP.md](./SETUP.md#deployment) for production details.

---

## 🔐 Security Checklist

- [ ] Change default Neo4j password
- [ ] Set Redis password
- [ ] Use HTTPS in production
- [ ] Enable authentication (JWT)
- [ ] Validate file uploads
- [ ] Add rate limiting
- [ ] Set CORS correctly
- [ ] Enable request logging
- [ ] Use secrets management
- [ ] Regular security audits

---

## 📊 Performance Optimization

### Database
- Create indexes on frequently queried fields
- Enable query caching
- Optimize vector search parameters

### Backend
- Increase Celery worker processes
- Use connection pooling
- Cache embeddings model in memory

### Frontend
- Enable caching headers
- Lazy load components
- Optimize bundle size

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Open Pull Request

### Code Style
- Python: PEP 8 (use `black` formatter)
- JavaScript: ESLint + Prettier
- Comments for complex logic

---

## 📚 Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Neo4j Docs](https://neo4j.com/docs/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [React Docs](https://react.dev/)
- [Celery Docs](https://docs.celeryproject.io/)

### Tutorials
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Neo4j Graph Academy](https://graphacademy.neo4j.com/)
- [React Tutorial](https://react.dev/learn)

### Tools
- [Neo4j Browser](http://localhost:7474) - Query interface
- [Qdrant Dashboard](http://localhost:6333/dashboard) - Vector DB UI
- [OpenAPI Docs](http://localhost:8000/docs) - API explorer
- [Redux DevTools](https://github.com/reduxjs/redux-devtools) - State debugging

---

## 🎯 Roadmap

### Version 1.1
- [ ] User authentication (JWT)
- [ ] Document sharing
- [ ] Advanced search filters

### Version 1.2
- [ ] OCR for scanned PDFs
- [ ] Multi-language support
- [ ] Real-time collaboration

### Version 2.0
- [ ] Mobile app (React Native)
- [ ] Document comparison
- [ ] Export functionality
- [ ] Batch processing API

---

## 🐛 Known Issues

| Issue | Status | Workaround |
|-------|--------|-----------|
| Large PDF timeout | Open | Increase worker timeout |
| Vector dimension mismatch | Fixed | v1.0.2 |
| CORS errors in dev | Known | Use proxy in vite.config.js |

---

## 📞 Support

- **Issues**: [GitHub Issues](../issues)
- **Discussions**: [GitHub Discussions](../discussions)
- **Email**: support@example.com
- **Docs**: See [README.md](./README.md)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 📋 Quick Navigation

- **New? Start here:** [QUICKSTART.md](./QUICKSTART.md)
- **Setup guide:** [SETUP.md](./SETUP.md)
- **API docs:** [API_REFERENCE.md](./API_REFERENCE.md)
- **Frontend guide:** [frontend/README.md](./frontend/README.md)
- **Project overview:** [README.md](./README.md)

---

**Last Updated:** March 31, 2026
**Version:** 1.0.0
**Maintainer:** PDF Document Intelligence Team

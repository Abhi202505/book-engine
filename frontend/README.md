# PDF Document Intelligence - Frontend

React + Vite frontend for PDF document parsing, embedding, and visualization.

## Features

- 📤 **File Upload**: Upload PDF documents for processing
- 📖 **Document Viewer**: View parsed paragraphs and metadata
- 🔍 **Search**: Semantic search across documents using embeddings
- 📊 **Visualization**: Grid-based document layout with rich metadata display
- ⚡ **Real-time Processing**: Track document processing status in real-time

## Quick Start

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

Output will be in the `dist/` directory.

## Architecture

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # API integration & HTTP client
│   ├── components/
│   │   ├── FileUpload.jsx     # PDF upload interface
│   │   └── DocumentViewer.jsx # Document display & search
│   ├── styles/
│   │   ├── App.css
│   │   ├── FileUpload.css
│   │   └── DocumentViewer.css
│   ├── App.jsx                # Main app component
│   └── main.jsx               # React entry point
└── index.html
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- **POST** `/api/v1/upload` - Upload PDF file
- **GET** `/api/v1/task/{taskId}` - Get processing status
- **GET** `/api/v1/documents/{bookId}` - Get document paragraphs
- **GET** `/api/v1/documents/{bookId}/search` - Search documents

## Workflow

1. User uploads PDF file
2. Backend processes document (parsing, embedding, ingestion)
3. Frontend polls task status
4. Once complete, user can view and search document
5. Results displayed with metadata and similarity scores

## Backend Requirements

Ensure the backend is running from the project root folder:

```bash
cd ..
# Activate your venv first (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# Or on macOS/Linux:
# source .venv/bin/activate
python main.py

# In a second terminal, stay in the project root and start Celery
cd ..
.\.venv\Scripts\python.exe celery_worker.py
```

Required services:
- FastAPI server on port 8000
- Celery worker for background tasks
- Neo4j database (port 7687)
- Qdrant vector database (port 6333)
- Redis (port 6379)

## Configuration

Copy `.env.example` to `.env` and update:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Technologies

- **React 18** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS3** - Styling with gradients and animations

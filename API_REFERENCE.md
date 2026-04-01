# Backend API Reference

## Overview

The backend API provides document processing, storage, and retrieval capabilities. It integrates with:
- **Neo4j**: Graph database for structured document relationships
- **Qdrant**: Vector database for semantic search
- **Redis/Celery**: Background task processing

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Upload Document
Upload a PDF file for processing.

**Endpoint:** `POST /api/v1/upload`

**Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <PDF file>
```

**Response:**
```json
{
  "message": "Document accepted for processing",
  "book_id": "doc_9d4a54da",
  "task_id": "abc123def456"
}
```

**Status Codes:**
- `200`: Document accepted for processing
- `400`: Invalid file format
- `500`: Server error

---

### 2. Get Task Status
Check the processing status of an uploaded document.

**Endpoint:** `GET /api/v1/task/{task_id}`

**Parameters:**
- `task_id` (string, required): Task ID from upload response

**Response:**
```json
{
  "task_id": "abc123def456",
  "status": "SUCCESS",
  "result": {
    "status": "SUCCESS",
    "book_id": "doc_9d4a54da"
  }
}
```

**Status Values:**
- `PENDING`: Task is waiting to be processed
- `PROGRESS`: Task is currently processing
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed

**Response Codes:**
- `200`: Status retrieved
- `404`: Task not found

---

### 3. Get Document Paragraphs
Retrieve all parsed paragraphs from a processed document.

**Endpoint:** `GET /api/v1/documents/{book_id}`

**Parameters:**
- `book_id` (string, required): Document ID from upload response

**Response:**
```json
{
  "book_id": "doc_9d4a54da",
  "total": 49,
  "paragraphs": [
    {
      "id": "para_001",
      "text": "The introduction discusses...",
      "page_number": 1,
      "type": "paragraph"
    },
    ...
  ]
}
```

**Response Codes:**
- `200`: Paragraphs retrieved
- `400`: Book not found

---

### 4. Search Document
Perform semantic search across document paragraphs using vector similarity.

**Endpoint:** `GET /api/v1/documents/{book_id}/search`

**Parameters:**
- `book_id` (string, required): Document ID
- `q` (string, required, min_length=1): Search query

**Query Example:**
```
GET /api/v1/documents/doc_9d4a54da/search?q=machine learning applications
```

**Response:**
```json
{
  "query": "machine learning applications",
  "book_id": "doc_9d4a54da",
  "results": [
    {
      "id": "chunk_042",
      "text": "Machine learning is widely used in...",
      "page_number": 15,
      "similarity_score": 0.87
    },
    ...
  ]
}
```

**Response Codes:**
- `200`: Search completed
- `400`: Invalid query parameters
- `404`: Document not found

---

## Data Models

### Paragraph Object
```json
{
  "id": "string",
  "text": "string",
  "page_number": "integer",
  "type": "string",
  "similarity_score": "number (only in search results)"
}
```

### Search Result
```json
{
  "id": "string",
  "text": "string",
  "page_number": "integer",
  "similarity_score": "number (0-1)"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

| Code | Message | Cause |
|------|---------|-------|
| 400 | Invalid file type | Only PDF files are supported |
| 404 | Document not found | Book ID doesn't exist in database |
| 422 | Validation error | Missing or invalid query parameters |
| 500 | Internal server error | Backend service failure |

---

## CORS Configuration

The API supports CORS for the frontend application:
- **Allowed Origins:** `http://localhost:3000`, `localhost:3000`
- **Allowed Methods:** All HTTP methods
- **Allowed Headers:** All headers
- **Credentials:** Allowed

---

## Rate Limiting

Currently no rate limiting is enabled. In production, it's recommended to add:
- Per-IP rate limits
- Per-user rate limits for authenticated endpoints
- Search query throttling

---

## Processing Pipeline

1. **Upload** → Document received and queued
2. **Parse** → PDF analyzed using layout parser
3. **Embed** → Text converted to vectors
4. **Store** → Data ingested into Neo4j and Qdrant
5. **Ready** → Document available for search and retrieval

Typical processing time: 10-30 seconds per document

---

## Integration Examples

### Python (Requests)
```python
import requests

# Upload
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/v1/upload', files=files)
task_id = response.json()['task_id']

# Check status
status = requests.get(f'http://localhost:8000/api/v1/task/{task_id}')
print(status.json())

# Get document
doc = requests.get(f'http://localhost:8000/api/v1/documents/{response.json()["book_id"]}')
print(doc.json())
```

### JavaScript (Fetch)
```javascript
// Upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
const uploadRes = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  body: formData
});
const { task_id, book_id } = await uploadRes.json();

// Check status
const statusRes = await fetch(`http://localhost:8000/api/v1/task/${task_id}`);
console.log(await statusRes.json());

// Get document
const docRes = await fetch(`http://localhost:8000/api/v1/documents/${book_id}`);
console.log(await docRes.json());
```

---

## Deployment Considerations

- Ensure all required services (Neo4j, Qdrant, Redis) are running
- Set appropriate environment variables for database credentials
- Configure CORS for production domain
- Implement authentication/authorization for API endpoints
- Add request logging and monitoring
- Set up proper error tracking and alerting

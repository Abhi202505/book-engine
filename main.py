import uuid
from fastapi import FastAPI, UploadFile, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from celery import Celery
import shutil
import os

app = FastAPI(title="Distributed Document Intelligence API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Celery Configuration (Redis as broker)
celery_app = Celery("doc_tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

@celery_app.task(bind=True)
def process_pdf_task(self, pdf_path: str, book_id: str):
    try:
        import sys
        import os

        # Force Python to look in the current folder for modules
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        # Try to import required modules
        try:
            from pdf_parser import PDFLayoutParser
            from graph_builder import Neo4jIngestor
            from vector_store import QdrantIngestor
        except ImportError as e:
            raise Exception(f"Missing required modules: {str(e)}. Please ensure all dependencies are installed.")

        # Update task state
        self.update_state(state='PROGRESS', meta={'message': 'Parsing PDF...'})

        # 1. Parse PDF via GPU-ready Layout logic
        parser = PDFLayoutParser(pdf_path=pdf_path, book_id=book_id)
        json_output = parser.parse()

        self.update_state(state='PROGRESS', meta={'message': 'Ingesting to databases...'})

        # 2. Ingest to Neo4j
        try:
            graph_db = Neo4jIngestor("bolt://localhost:7687", "neo4j", "password")
            graph_db.ingest_document(json_output)
            graph_db.close()
        except Exception as e:
            raise Exception(f"Neo4j ingestion failed: {str(e)}. Please ensure Neo4j is running.")

        # 3. Ingest to Qdrant
        try:
            vector_db = QdrantIngestor()
            vector_db.ingest_document(json_output)
        except Exception as e:
            raise Exception(f"Qdrant ingestion failed: {str(e)}. Please ensure Qdrant is running.")

        # Clean up file with retry logic for Windows file lock issues
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                os.remove(pdf_path)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait 1 second before retry
                else:
                    import logging
                    logging.warning(f"Could not delete {pdf_path} after {max_retries} attempts. File may be locked.")

        return {"status": "SUCCESS", "book_id": book_id}

    except Exception as e:
        # Log the error and re-raise it so Celery captures it
        import logging
        logging.error(f"Task {self.request.id} failed: {str(e)}")
        raise e


@app.post("/api/v1/upload")
async def upload_document(file: UploadFile):
    book_id = f"doc_{uuid.uuid4().hex[:8]}"
    file_path = f"{book_id}.pdf"  # <--- FIX: Saves in your current folder
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Dispatch Async Celery Task
    task = process_pdf_task.delay(file_path, book_id)
    
    return {
        "message": "Document accepted for processing",
        "book_id": book_id,
        "task_id": task.id
    }


@app.get("/api/v1/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background processing task"""
    task = celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result
    elif task.failed():
        # Provide better error information
        if task.info:
            response["result"] = str(task.info)
        else:
            response["result"] = "Task failed with unknown error"
    else:
        response["result"] = None

    return response


@app.get("/api/v1/documents/{book_id}")
async def get_document(book_id: str):
    """Retrieve all paragraphs and metadata from Neo4j for a document"""
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from graph_builder import Neo4jIngestor
        
        graph_db = Neo4jIngestor("bolt://localhost:7687", "neo4j", "password")
        paragraphs = graph_db.query_paragraphs(book_id)
        graph_db.close()
        
        return {
            "book_id": book_id,
            "total": len(paragraphs),
            "paragraphs": paragraphs
        }
        
    except Exception as e:
        return {
            "book_id": book_id,
            "error": str(e),
            "paragraphs": []
        }


@app.get("/api/v1/documents/{book_id}/search")
async def search_document(book_id: str, q: str = Query(..., min_length=1)):
    """Search documents using semantic similarity with Qdrant"""
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from vector_store import QdrantIngestor
        from sentence_transformers import SentenceTransformer
        
        # Get embedding for search query
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(q).tolist()
        
        # Search in Qdrant
        vector_db = QdrantIngestor()
        results = vector_db.search(
            query_embedding=query_embedding,
            limit=10,
            filters={"book_id": book_id}
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "page_number": result.payload.get("page_number"),
                "similarity_score": result.score
            })
        
        return {
            "query": q,
            "book_id": book_id,
            "results": formatted_results
        }
        
    except Exception as e:
        return {
            "query": q,
            "book_id": book_id,
            "error": str(e),
            "results": []
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
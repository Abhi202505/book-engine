from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import json
import numpy as np

class QdrantIngestor:
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "document_chunks"
        
        # Ensure collection exists
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )

    def _mock_gpu_embedding(self, text: str) -> list:
        """Mock: Replace with SentenceTransformers or external GPU service (e.g., MinerU/BGE)"""
        return np.random.rand(768).tolist()

    def ingest_document(self, json_data: str):
        doc = json.loads(json_data)
        points = []
        
        for page in doc["pages"]:
            for section in page["sections"]:
                for block in section["content"]:
                    if block.get("embedding_ready") and block.get("text"):
                        # Intelligent Chunking: Prefix with section title for deep context
                        context_text = f"Section: {section['title']}\n\n{block['text']}"
                        vector = self._mock_gpu_embedding(context_text)
                        
                        points.append(
                            PointStruct(
                                id=block["id"],
                                vector=vector,
                                payload={
                                    "book_id": doc["book_id"],
                                    "page_number": page["page_number"],
                                    "section_title": section["title"],
                                    "type": block["type"],
                                    "text": context_text
                                }
                            )
                        )
        
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Upserted {len(points)} chunks to Qdrant.")

    def search(self, query_embedding: list, limit: int = 10, filters: dict = None):
        """Search for similar vectors in Qdrant"""
        try:
            # Build filter if book_id provided
            query_filter = None
            if filters and "book_id" in filters:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="book_id",
                            match=MatchValue(value=filters["book_id"])
                        )
                    ]
                )
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
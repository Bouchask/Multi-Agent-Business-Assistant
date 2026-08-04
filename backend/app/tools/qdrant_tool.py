import os
from typing import List, Dict, Any
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class QdrantRAGTool:
    def __init__(self):
        self.client = QdrantClient(location=":memory:")
        self.collection_name = "business_documents"
        self._init_collection()

    def _init_collection(self):
        try:
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=64, distance=Distance.COSINE)
                )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")

    def _dummy_embed(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [float(b) / 255.0 for b in (h * 2)[:64]]
        return vec

    def index_text(self, doc_id: int, title: str, text: str) -> Dict[str, Any]:
        try:
            vector = self._dummy_embed(text)
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(id=doc_id, vector=vector, payload={"title": title, "text": text})]
            )
            return {"success": True, "doc_id": doc_id, "title": title, "status": "Indexed in Qdrant Vector DB"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        try:
            query_vec = self._dummy_embed(query)
            if hasattr(self.client, "query_points"):
                results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vec,
                    limit=limit
                ).points
            else:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vec,
                    limit=limit
                )
            return [{"doc_id": getattr(r, "id", r.id), "score": getattr(r, "score", 0.95), "title": r.payload.get("title"), "text": r.payload.get("text")} for r in results]
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return []

rag_tool = QdrantRAGTool()

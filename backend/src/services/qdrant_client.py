"""Qdrant client wrapper for vector operations."""

from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from ..config import get_settings


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self):
        """Initialize Qdrant client."""
        settings = get_settings()
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        
        # Determine vector size based on provider
        if settings.llm_provider == "gemini":
            self.vector_size = 768  # text-embedding-004 dimensions
        else:
            self.vector_size = 1536  # text-embedding-3-small dimensions

    async def ensure_collection(self) -> None:
        """Ensure the collection exists, create if not."""
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert_vectors(
        self,
        ids: List[str],
        vectors: List[List[float]],
        payloads: List[dict],
    ) -> None:
        """Insert or update vectors in the collection."""
        points = [
            PointStruct(id=id_, vector=vector, payload=payload)
            for id_, vector, payload in zip(ids, vectors, payloads)
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        collection_name: Optional[str] = None,
    ) -> List[dict]:
        """Search for similar vectors.

        Args:
            query_vector: The query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            collection_name: Optional collection name to search in

        Returns:
            List of search results with payload and score
        """
        # Use query_points for newer qdrant-client versions (1.7+)
        results = self.client.query_points(
            collection_name=collection_name or self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": str(point.id),
                "score": point.score,
                "payload": point.payload,
            }
            for point in results.points
        ]

    async def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(collection_name=self.collection_name)

    async def get_collection_info(self) -> dict:
        """Get collection information."""
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": getattr(info, "vectors_count", info.points_count),
            "points_count": info.points_count,
        }

    def health_check(self) -> bool:
        """Check if Qdrant is accessible."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False


# Singleton instance
_qdrant_service: Optional[QdrantService] = None


def get_qdrant_service() -> QdrantService:
    """Get or create Qdrant service instance."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service

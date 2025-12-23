"""RAG retrieval service for book-grounded Q&A.

T026 [US1] - Handles vector similarity search, confidence filtering,
and context aggregation for RAG responses.
"""

import logging
from dataclasses import dataclass
from typing import Any

from ..config import get_settings
from .openai_client import OpenAIClient
from .qdrant_client import QdrantService

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """Represents a retrieved book chunk with metadata."""

    id: str
    text: str
    score: float
    chapter: str
    section: str | None
    page: int | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "score": self.score,
            "chapter": self.chapter,
            "section": self.section,
            "page": self.page,
        }


@dataclass
class SourceReference:
    """Represents a source citation."""

    chapter: str
    section: str | None
    page: int | None
    relevance: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "chapter": self.chapter,
            "relevance": self.relevance,
        }
        if self.section:
            result["section"] = self.section
        if self.page:
            result["page"] = self.page
        return result


class RAGService:
    """Service for RAG retrieval operations."""

    NOT_COVERED_MESSAGE = (
        "This topic is not covered in this book. The book focuses on the "
        "specific technical content that has been indexed. You might want "
        "to consult other resources for information about this topic."
    )

    def __init__(
        self,
        qdrant_client: QdrantService,
        openai_client: OpenAIClient,
        confidence_threshold: float | None = None,
        collection_name: str | None = None,
    ):
        """Initialize RAG service.

        Args:
            qdrant_client: Qdrant client for vector search.
            openai_client: OpenAI client for embeddings.
            confidence_threshold: Minimum score for relevant results.
            collection_name: Qdrant collection name.
        """
        self.qdrant_client = qdrant_client
        self.openai_client = openai_client

        settings = get_settings()
        self.confidence_threshold = confidence_threshold or settings.confidence_threshold
        self.collection_name = collection_name or settings.qdrant_collection_name

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant book chunks for a query.

        Args:
            query: User's question.
            top_k: Maximum number of chunks to retrieve.

        Returns:
            List of chunks with score >= confidence_threshold.
        """
        logger.info(f"RAGService.retrieve_relevant_chunks called: query='{query[:50]}...', top_k={top_k}")

        if not query or not query.strip():
            logger.warning("Empty query received, returning empty chunks")
            return []

        # Get query embedding
        try:
            logger.info("Creating query embedding...")
            query_embedding = await self.openai_client.create_embedding(query)
            logger.info(f"Query embedding created: length={len(query_embedding)}")
        except Exception as e:
            logger.error(f"Failed to create embedding: {type(e).__name__}: {e}", exc_info=True)
            raise

        # Search Qdrant
        try:
            logger.info(f"Searching Qdrant collection '{self.collection_name}'...")
            results = await self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )
            logger.info(f"Qdrant search returned {len(results)} results")
        except Exception as e:
            logger.error(f"Qdrant search failed: {type(e).__name__}: {e}", exc_info=True)
            raise

        # Filter by confidence threshold
        chunks = []
        for result in results:
            if result["score"] >= self.confidence_threshold:
                payload = result.get("payload", {})
                chunk = RetrievedChunk(
                    id=str(result["id"]),
                    text=payload.get("text", ""),
                    score=result["score"],
                    chapter=payload.get("chapter", "Unknown"),
                    section=payload.get("section"),
                    page=payload.get("page"),
                )
                chunks.append(chunk)
            else:
                logger.debug(f"Chunk {result['id']} filtered out: score={result['score']} < threshold={self.confidence_threshold}")

        logger.info(f"Filtered to {len(chunks)} chunks above confidence threshold {self.confidence_threshold}")
        return chunks

    async def is_query_covered(self, query: str) -> bool:
        """Check if query can be answered from book content.

        Args:
            query: User's question.

        Returns:
            True if relevant content exists, False otherwise.
        """
        chunks = await self.retrieve_relevant_chunks(query, top_k=1)
        return len(chunks) > 0

    def build_context(self, chunks: list[RetrievedChunk]) -> str:
        """Build context string from retrieved chunks.

        Args:
            chunks: List of retrieved chunks.

        Returns:
            Formatted context string for the prompt.
        """
        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            # Format source info
            source_info = f"[{chunk.chapter}"
            if chunk.section:
                source_info += f", {chunk.section}"
            if chunk.page:
                source_info += f", Page {chunk.page}"
            source_info += "]"

            context_parts.append(f"--- Source {i} {source_info} ---\n{chunk.text}")

        return "\n\n".join(context_parts)

    def extract_sources(
        self, chunks: list[RetrievedChunk]
    ) -> list[SourceReference]:
        """Extract source references from chunks.

        Args:
            chunks: List of retrieved chunks.

        Returns:
            List of source references for citation.
        """
        # Deduplicate by chapter+section
        seen = set()
        sources = []

        for chunk in chunks:
            key = (chunk.chapter, chunk.section)
            if key not in seen:
                seen.add(key)
                sources.append(
                    SourceReference(
                        chapter=chunk.chapter,
                        section=chunk.section,
                        page=chunk.page,
                        relevance=chunk.score,
                    )
                )

        return sources

    def get_not_covered_response(self) -> str:
        """Get the standard 'not covered' response message.

        Returns:
            The not covered message.
        """
        return self.NOT_COVERED_MESSAGE


def get_rag_service() -> RAGService:
    """FastAPI dependency to get RAG service instance.

    Returns:
        Configured RAGService instance.
    """
    from .openai_client import get_openai_client
    from .qdrant_client import get_qdrant_service

    return RAGService(
        qdrant_client=get_qdrant_service(),
        openai_client=get_openai_client(),
    )


def create_rag_service(
    qdrant_client: "QdrantService | None" = None,
    openai_client: "OpenAIClient | None" = None,
) -> RAGService:
    """Factory function to create RAG service instance with custom dependencies.

    Use this for testing or custom configurations.

    Args:
        qdrant_client: Optional Qdrant client (created if not provided).
        openai_client: Optional OpenAI client (created if not provided).

    Returns:
        Configured RAGService instance.
    """
    from .openai_client import get_openai_client
    from .qdrant_client import get_qdrant_service

    if qdrant_client is None:
        qdrant_client = get_qdrant_service()
    if openai_client is None:
        openai_client = get_openai_client()

    return RAGService(
        qdrant_client=qdrant_client,
        openai_client=openai_client,
    )

"""Embedding service for text processing."""

from typing import List

import tiktoken

from ..config import get_settings
from .openai_client import get_openai_service


class EmbeddingService:
    """Service for creating and managing text embeddings."""

    def __init__(self):
        """Initialize embedding service."""
        self.openai = get_openai_service()
        settings = get_settings()
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        # Use cl100k_base encoding for text-embedding-3-small
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str, metadata: dict = None) -> List[dict]:
        """Split text into overlapping chunks.

        Args:
            text: Text to chunk
            metadata: Optional metadata to include with each chunk

        Returns:
            List of chunk dicts with content and metadata
        """
        tokens = self.tokenizer.encode(text)
        chunks = []
        chunk_index = 0

        i = 0
        while i < len(tokens):
            # Get chunk of tokens
            chunk_tokens = tokens[i : i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            chunk_data = {
                "content": chunk_text,
                "chunk_index": chunk_index,
                "token_count": len(chunk_tokens),
            }

            if metadata:
                chunk_data.update(metadata)

            chunks.append(chunk_data)

            # Move forward with overlap
            i += self.chunk_size - self.chunk_overlap
            chunk_index += 1

        return chunks

    async def embed_text(self, text: str) -> List[float]:
        """Create embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return await self.openai.create_embedding(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return await self.openai.create_embeddings(texts)

    async def embed_chunks(self, chunks: List[dict]) -> List[dict]:
        """Add embeddings to chunks.

        Args:
            chunks: List of chunk dicts with 'content' key

        Returns:
            Chunks with added 'embedding' key
        """
        texts = [chunk["content"] for chunk in chunks]
        embeddings = await self.embed_texts(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        return chunks


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

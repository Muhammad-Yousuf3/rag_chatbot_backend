#!/usr/bin/env python3
"""Book content ingestion script for Qdrant indexing."""

import argparse
import asyncio
import hashlib
import re
from pathlib import Path
from typing import List

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.embedding_service import get_embedding_service
from src.services.qdrant_client import get_qdrant_service


def extract_chapter_info(file_path: Path, content: str) -> dict:
    """Extract chapter metadata from file path and content.

    Args:
        file_path: Path to the markdown file
        content: File content

    Returns:
        Chapter metadata dict
    """
    # Get chapter slug from filename, including parent dir to avoid collisions
    # e.g. "01-nervous-system_00-intro"
    slug = f"{file_path.parent.name}_{file_path.stem}"

    # Try to extract title from first H1 heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem.replace("-", " ").title()

    # Extract sections (H2 headings)
    sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)

    return {
        "chapter_slug": slug,
        "title": title,
        "sections": sections,
        "file_path": str(file_path),
    }


def generate_chunk_id(chapter_slug: str, chunk_index: int) -> str:
    """Generate unique ID for a chunk.

    Args:
        chapter_slug: Chapter identifier
        chunk_index: Index of chunk within chapter

    Returns:
        Unique chunk ID
    """
    raw = f"{chapter_slug}:{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


async def process_markdown_file(
    file_path: Path,
    embedding_service,
) -> List[dict]:
    """Process a single markdown file into chunks with embeddings.

    Args:
        file_path: Path to markdown file
        embedding_service: Embedding service instance

    Returns:
        List of chunk dicts ready for Qdrant
    """
    content = file_path.read_text(encoding="utf-8")

    # Skip empty files
    if not content.strip():
        print(f"  Skipping empty file: {file_path}")
        return []

    # Extract chapter info
    chapter_info = extract_chapter_info(file_path, content)
    print(f"  Processing: {chapter_info['title']}")

    # Create chunks
    chunks = embedding_service.chunk_text(
        content,
        metadata={
            "chapter_slug": chapter_info["chapter_slug"],
            "title": chapter_info["title"],
        },
    )

    print(f"    Created {len(chunks)} chunks")

    # Add embeddings
    chunks = await embedding_service.embed_chunks(chunks)

    # Prepare for Qdrant
    result = []
    for chunk in chunks:
        chunk_id = generate_chunk_id(
            chapter_info["chapter_slug"],
            chunk["chunk_index"],
        )
        result.append({
            "id": chunk_id,
            "vector": chunk["embedding"],
            "payload": {
                "chapter_slug": chunk["chapter_slug"],
                "title": chunk["title"],
                "content": chunk["content"],
                "chunk_index": chunk["chunk_index"],
            },
        })

    return result


async def ingest_book(
    source_dir: Path,
    clear: bool = False,
) -> None:
    """Ingest book content from markdown files.

    Args:
        source_dir: Directory containing markdown files
        clear: Whether to clear existing collection
    """
    print(f"Ingesting book content from: {source_dir}")

    # Initialize services
    embedding_service = get_embedding_service()
    qdrant_service = get_qdrant_service()

    # Clear collection if requested
    if clear:
        print("Clearing existing collection...")
        try:
            await qdrant_service.delete_collection()
        except Exception:
            pass  # Collection may not exist

    # Ensure collection exists
    print("Ensuring Qdrant collection exists...")
    await qdrant_service.ensure_collection()

    # Find all markdown files
    md_files = list(source_dir.glob("**/*.md"))
    md_files = [f for f in md_files if not f.name.startswith("_")]

    if not md_files:
        print(f"No markdown files found in {source_dir}")
        return

    print(f"Found {len(md_files)} markdown files")

    # Process each file
    all_chunks = []
    for file_path in md_files:
        chunks = await process_markdown_file(file_path, embedding_service)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("No chunks to upload")
        return

    # Upload to Qdrant in batches
    batch_size = 100
    print(f"\nUploading {len(all_chunks)} chunks to Qdrant...")

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        await qdrant_service.upsert_vectors(
            ids=[c["id"] for c in batch],
            vectors=[c["vector"] for c in batch],
            payloads=[c["payload"] for c in batch],
        )
        print(f"  Uploaded batch {i // batch_size + 1}/{(len(all_chunks) + batch_size - 1) // batch_size}")

    # Print summary
    info = await qdrant_service.get_collection_info()
    print(f"\nIngestion complete!")
    print(f"  Collection: {info['name']}")
    print(f"  Total vectors: {info['vectors_count']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest book content into Qdrant vector database"
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Directory containing markdown files",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing collection before ingesting",
    )

    args = parser.parse_args()

    if not args.source.exists():
        print(f"Error: Source directory does not exist: {args.source}")
        sys.exit(1)

    asyncio.run(ingest_book(args.source, args.clear))


if __name__ == "__main__":
    main()

"""Translation service with caching.

T058 [US3] - Handles translation requests with database caching
and progress tracking.
"""

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.translate_agent import TranslateAgent, get_translate_agent
from ..models.translation import Translation, TranslationStatus


@dataclass
class TranslationResult:
    """Result of a translation request."""

    chapter_slug: str
    language: str
    status: str
    content: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
    estimated_seconds: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            "chapter_slug": self.chapter_slug,
            "language": self.language,
            "status": self.status,
        }

        if self.content:
            result["content"] = self.content
        if self.created_at:
            result["created_at"] = self.created_at
        if self.completed_at:
            result["completed_at"] = self.completed_at
        if self.error_message:
            result["error_message"] = self.error_message
        if self.estimated_seconds is not None:
            result["estimated_seconds"] = self.estimated_seconds

        return result


class TranslationService:
    """Service for managing chapter translations with caching."""

    SUPPORTED_LANGUAGES = {"ur": "Urdu"}

    def __init__(
        self,
        translate_agent: TranslateAgent | None = None,
    ):
        """Initialize translation service.

        Args:
            translate_agent: Translation agent instance.
        """
        self.translate_agent = translate_agent or get_translate_agent()

    async def get_translation(
        self,
        db: AsyncSession,
        chapter_slug: str,
        language: str = "ur",
    ) -> TranslationResult:
        """Get translation for a chapter.

        Args:
            db: Database session.
            chapter_slug: Chapter identifier.
            language: Target language code.

        Returns:
            TranslationResult with status and content if available.
        """
        if not chapter_slug:
            raise ValueError("chapter_slug is required")

        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

        # Check for existing translation
        result = await db.execute(
            select(Translation).where(
                Translation.chapter_slug == chapter_slug,
                Translation.language == language,
            )
        )
        translation = result.scalar_one_or_none()

        if translation:
            return TranslationResult(
                chapter_slug=translation.chapter_slug,
                language=translation.language,
                status=translation.status.value,
                content=translation.content if translation.status == TranslationStatus.COMPLETED else None,
                created_at=translation.created_at.isoformat() if translation.created_at else None,
                completed_at=translation.completed_at.isoformat() if translation.completed_at else None,
                error_message=translation.error_message if translation.status == TranslationStatus.FAILED else None,
            )

        # No translation exists
        return TranslationResult(
            chapter_slug=chapter_slug,
            language=language,
            status="not_found",
        )

    async def request_translation(
        self,
        db: AsyncSession,
        chapter_slug: str,
        content: str,
        language: str = "ur",
    ) -> TranslationResult:
        """Request translation for a chapter.

        Args:
            db: Database session.
            chapter_slug: Chapter identifier.
            content: Original content to translate.
            language: Target language code.

        Returns:
            TranslationResult with status.
        """
        if not chapter_slug:
            raise ValueError("chapter_slug is required")

        if not content or not content.strip():
            raise ValueError("content is required")

        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

        # Check for existing translation
        existing = await self.get_translation(db, chapter_slug, language)
        if existing.status == "completed":
            return existing

        # Check if translation is in progress
        if existing.status in ["pending", "in_progress"]:
            return existing

        # Create new translation record
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        translation_id = str(uuid.uuid4())

        translation = Translation(
            id=translation_id,
            chapter_slug=chapter_slug,
            language=language,
            status=TranslationStatus.IN_PROGRESS,
            original_hash=content_hash,
        )
        db.add(translation)
        await db.commit()

        # Perform translation
        try:
            translated_content = await self.translate_agent.translate_chunked(
                content=content,
                target_language=language,
            )

            # Update translation with result
            translation.content = translated_content
            translation.status = TranslationStatus.COMPLETED
            translation.completed_at = datetime.utcnow()
            await db.commit()

            return TranslationResult(
                chapter_slug=chapter_slug,
                language=language,
                status="completed",
                content=translated_content,
                created_at=translation.created_at.isoformat(),
                completed_at=translation.completed_at.isoformat(),
            )

        except Exception as e:
            # Mark translation as failed
            translation.status = TranslationStatus.FAILED
            translation.error_message = str(e)
            await db.commit()

            return TranslationResult(
                chapter_slug=chapter_slug,
                language=language,
                status="failed",
                error_message=str(e),
            )

    async def get_translation_progress(
        self,
        db: AsyncSession,
        chapter_slug: str,
        language: str = "ur",
    ) -> dict[str, Any]:
        """Get translation progress for a chapter.

        Args:
            db: Database session.
            chapter_slug: Chapter identifier.
            language: Target language code.

        Returns:
            Progress information dictionary.
        """
        result = await self.get_translation(db, chapter_slug, language)

        return {
            "chapter_slug": chapter_slug,
            "language": language,
            "status": result.status,
            "estimated_seconds": self._estimate_time(result.status),
        }

    def _estimate_time(self, status: str) -> int | None:
        """Estimate remaining time based on status.

        Args:
            status: Current translation status.

        Returns:
            Estimated seconds remaining or None.
        """
        estimates = {
            "pending": 60,
            "in_progress": 30,
            "completed": 0,
            "failed": None,
            "not_found": None,
        }
        return estimates.get(status)


def get_translation_service() -> TranslationService:
    """FastAPI dependency to get translation service instance.

    Returns:
        Configured TranslationService instance.
    """
    return TranslationService()

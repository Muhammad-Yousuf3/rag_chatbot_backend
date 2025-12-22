"""Personalization service for experience-level-aware responses.

T077-T079 [US4] - Implements personalization context and prompt generation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User, UserPreference


class ExperienceLevel(str, Enum):
    """User experience level enum."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class PersonalizationContext:
    """Context for personalizing responses."""

    user_id: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    chapters_read: List[str] = field(default_factory=list)
    preferred_language: str = "en"

    def to_prompt_context(self) -> str:
        """Convert to prompt context string.

        Returns:
            Context string for prompt augmentation.
        """
        level_descriptions = {
            ExperienceLevel.BEGINNER: (
                "The user is a beginner. Use simple, clear explanations "
                "with examples. Avoid jargon and technical terms when possible. "
                "Break down complex concepts into smaller, digestible pieces."
            ),
            ExperienceLevel.INTERMEDIATE: (
                "The user has intermediate knowledge. They are familiar with "
                "basic concepts. You can use some technical terms but explain "
                "advanced concepts when they appear."
            ),
            ExperienceLevel.ADVANCED: (
                "The user is advanced and has technical expertise. You can use "
                "technical terminology freely and provide detailed, in-depth "
                "explanations. Focus on nuances and advanced use cases."
            ),
        }

        context = level_descriptions.get(
            self.experience_level,
            level_descriptions[ExperienceLevel.BEGINNER],
        )

        if self.chapters_read:
            chapters_count = len(self.chapters_read)
            context += (
                f"\n\nThe user has read {chapters_count} chapter(s) from this book: "
                f"{', '.join(self.chapters_read[:5])}"
                + ("..." if chapters_count > 5 else "")
                + ". They may be familiar with content from these chapters."
            )

        return context


class PersonalizationService:
    """Service for managing user personalization."""

    async def get_user_context(
        self,
        db: AsyncSession,
        user_id: Optional[str],
    ) -> Optional[PersonalizationContext]:
        """Get personalization context for a user.

        Args:
            db: Database session.
            user_id: User ID (None for anonymous).

        Returns:
            PersonalizationContext if user found, None otherwise.
        """
        if not user_id:
            return None

        stmt = (
            select(User)
            .options(selectinload(User.preferences))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.preferences:
            return PersonalizationContext(
                user_id=user_id,
                experience_level=ExperienceLevel.BEGINNER,
            )

        return PersonalizationContext(
            user_id=user_id,
            experience_level=ExperienceLevel(user.preferences.experience_level.value),
            chapters_read=user.preferences.chapters_read or [],
            preferred_language=user.preferences.preferred_language or "en",
        )

    def get_default_context(self) -> PersonalizationContext:
        """Get default context for anonymous users.

        Returns:
            Default PersonalizationContext.
        """
        return PersonalizationContext()

    def generate_prompt_modifier(
        self,
        context: Optional[PersonalizationContext],
    ) -> str:
        """Generate prompt modifier based on personalization context.

        Args:
            context: Personalization context (None for anonymous).

        Returns:
            Prompt modifier string.
        """
        if not context:
            # Default for anonymous users
            return (
                "Provide clear, helpful explanations suitable for a general audience. "
                "Balance clarity with technical accuracy."
            )

        return context.to_prompt_context()

    async def track_chapter_read(
        self,
        db: AsyncSession,
        user_id: str,
        chapter_slug: str,
    ) -> None:
        """Track when a user reads a chapter.

        Args:
            db: Database session.
            user_id: User ID.
            chapter_slug: Chapter identifier.
        """
        stmt = (
            select(User)
            .options(selectinload(User.preferences))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.preferences:
            return

        current_chapters = user.preferences.chapters_read or []
        if chapter_slug not in current_chapters:
            user.preferences.chapters_read = current_chapters + [chapter_slug]
            await db.commit()

    async def update_experience_level(
        self,
        db: AsyncSession,
        user_id: str,
        level: ExperienceLevel,
    ) -> bool:
        """Update user's experience level.

        Args:
            db: Database session.
            user_id: User ID.
            level: New experience level.

        Returns:
            True if updated, False if user not found.
        """
        stmt = (
            select(User)
            .options(selectinload(User.preferences))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.preferences:
            return False

        user.preferences.experience_level = level
        await db.commit()
        await db.refresh(user)

        return True


# Singleton instance
_personalization_service: Optional[PersonalizationService] = None


def get_personalization_service() -> PersonalizationService:
    """Get or create PersonalizationService singleton.

    Returns:
        PersonalizationService instance.
    """
    global _personalization_service

    if _personalization_service is None:
        _personalization_service = PersonalizationService()

    return _personalization_service

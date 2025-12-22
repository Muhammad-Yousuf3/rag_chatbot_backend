"""User and UserPreference models.

T069-T070 [US4] - Database models for user authentication and preferences.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship

from src.db.database import Base

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class ExperienceLevel(str, enum.Enum):
    """User experience level for personalized responses."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class User(Base):
    """User model for authentication.

    Stores user credentials and links to preferences.
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    preferences = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email={self.email})>"


class UserPreference(Base):
    """User preferences for personalization.

    Stores experience level, reading history, and other preferences.
    """

    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    experience_level = Column(
        Enum(ExperienceLevel),
        default=ExperienceLevel.BEGINNER,
        nullable=False,
    )
    preferred_language = Column(String(10), default="en", nullable=False)
    chapters_read = Column(JSON, default=list, nullable=False)
    custom_settings = Column(JSON, default=dict, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        """String representation."""
        return f"<UserPreference(user_id={self.user_id}, level={self.experience_level})>"

    def add_chapter_read(self, chapter_slug: str) -> None:
        """Add a chapter to the read list if not already present.

        Args:
            chapter_slug: Chapter identifier to add.
        """
        if self.chapters_read is None:
            self.chapters_read = []

        if chapter_slug not in self.chapters_read:
            # Create new list to trigger SQLAlchemy change detection
            self.chapters_read = self.chapters_read + [chapter_slug]

    def get_chapters_read_count(self) -> int:
        """Get the number of chapters read.

        Returns:
            Number of unique chapters read.
        """
        return len(self.chapters_read) if self.chapters_read else 0

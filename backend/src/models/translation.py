"""Translation model for caching chapter translations.

T054 [US3] - Stores cached translations with metadata.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Index, JSON, String, Text

from ..db.database import Base


class TranslationStatus(str, enum.Enum):
    """Status of a translation request."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Translation(Base):
    """Model for cached chapter translations."""

    __tablename__ = "translations"

    id = Column(String(36), primary_key=True)
    chapter_slug = Column(String(255), nullable=False, index=True)
    language = Column(String(10), nullable=False, default="ur")
    status = Column(
        Enum(TranslationStatus),
        nullable=False,
        default=TranslationStatus.PENDING,
    )
    content = Column(Text, nullable=True)  # Translated content
    original_hash = Column(String(64), nullable=True)  # Hash of original content
    error_message = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)

    # Composite index for efficient lookup
    __table_args__ = (
        Index("ix_translations_chapter_language", "chapter_slug", "language"),
    )

    def __repr__(self) -> str:
        return f"<Translation {self.chapter_slug} ({self.language}) - {self.status.value}>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        result = {
            "id": self.id,
            "chapter_slug": self.chapter_slug,
            "language": self.language,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if self.status == TranslationStatus.COMPLETED:
            result["content"] = self.content
            result["completed_at"] = (
                self.completed_at.isoformat() if self.completed_at else None
            )
        elif self.status == TranslationStatus.FAILED:
            result["error_message"] = self.error_message

        return result

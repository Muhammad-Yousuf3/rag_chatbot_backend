"""Conversation model for chat sessions."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base

if TYPE_CHECKING:
    from src.models.message import Message
    from src.models.user import User


class ConversationMode(str, enum.Enum):
    """Conversation mode enum."""

    FULL_BOOK = "full_book"
    SELECTED_TEXT = "selected_text"


class Conversation(Base):
    """Conversation model representing a chat session."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    mode: Mapped[ConversationMode] = mapped_column(
        Enum(ConversationMode),
        default=ConversationMode.FULL_BOOK,
        nullable=False,
    )
    selected_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="conversations",
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, mode={self.mode})>"

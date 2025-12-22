"""Chat endpoint schemas.

Pydantic models for chat request/response validation.
T045 [US2] - Adds selected-text validation with min/max length.
"""

from pydantic import BaseModel, Field, field_validator


# Constants for validation
MIN_SELECTED_TEXT_LENGTH = 10
MAX_SELECTED_TEXT_LENGTH = 50000


class SourceReference(BaseModel):
    """Source citation reference."""

    chapter: str = Field(..., description="Chapter name or number")
    section: str | None = Field(None, description="Section within chapter")
    page: int | None = Field(None, description="Page number if available")
    relevance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score between 0 and 1"
    )


class ChatRequest(BaseModel):
    """Chat request payload."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message or question"
    )
    conversation_id: str | None = Field(
        None,
        description="Optional conversation ID for continuing a conversation"
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """Validate message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id_format(cls, v: str | None) -> str | None:
        """Validate conversation_id is a valid UUID format if provided."""
        if v is None:
            return v

        import uuid
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("conversation_id must be a valid UUID")


class SelectedTextRequest(BaseModel):
    """Selected-text chat request payload."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message or question about the selected text"
    )
    selected_text: str = Field(
        ...,
        min_length=MIN_SELECTED_TEXT_LENGTH,
        max_length=MAX_SELECTED_TEXT_LENGTH,
        description="The text selected by the user"
    )
    conversation_id: str | None = Field(
        None,
        description="Optional conversation ID for continuing a conversation"
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """Validate message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()

    @field_validator("selected_text")
    @classmethod
    def validate_selected_text(cls, v: str) -> str:
        """Validate selected text is not just whitespace and meets length requirements."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Selected text cannot be empty or whitespace only")
        if len(stripped) < MIN_SELECTED_TEXT_LENGTH:
            raise ValueError(
                f"Selected text must be at least {MIN_SELECTED_TEXT_LENGTH} characters"
            )
        if len(stripped) > MAX_SELECTED_TEXT_LENGTH:
            raise ValueError(
                f"Selected text cannot exceed {MAX_SELECTED_TEXT_LENGTH} characters"
            )
        return stripped

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id_format(cls, v: str | None) -> str | None:
        """Validate conversation_id is a valid UUID format if provided."""
        if v is None:
            return v

        import uuid
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("conversation_id must be a valid UUID")


class ChatResponse(BaseModel):
    """Chat response payload."""

    message: str = Field(..., description="Assistant's response message")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: list[SourceReference] = Field(
        default_factory=list,
        description="Source citations for the response"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Python is a high-level programming language...",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "sources": [
                        {
                            "chapter": "Chapter 1",
                            "section": "Introduction to Python",
                            "page": 1,
                            "relevance": 0.85
                        }
                    ]
                }
            ]
        }
    }

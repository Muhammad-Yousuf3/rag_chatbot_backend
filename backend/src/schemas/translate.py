"""Translation endpoint schemas.

Pydantic models for translation request/response validation.
"""

from pydantic import BaseModel, Field, field_validator


class TranslationRequest(BaseModel):
    """Translation request payload."""

    language: str = Field(
        default="ur",
        description="Target language code (default: ur for Urdu)"
    )
    content: str | None = Field(
        None,
        description="Content to translate (optional, uses chapter content if not provided)"
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language is supported."""
        supported = {"ur"}
        if v not in supported:
            raise ValueError(f"Unsupported language: {v}. Supported: {supported}")
        return v


class TranslationResponse(BaseModel):
    """Completed translation response."""

    chapter_slug: str = Field(..., description="Chapter identifier")
    language: str = Field(..., description="Target language code")
    content: str = Field(..., description="Translated content")
    created_at: str = Field(..., description="Translation creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chapter_slug": "chapter-1",
                    "language": "ur",
                    "content": "پائتھون ایک پروگرامنگ زبان ہے۔",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }


class TranslationPendingResponse(BaseModel):
    """Pending translation response."""

    chapter_slug: str = Field(..., description="Chapter identifier")
    language: str = Field(..., description="Target language code")
    status: str = Field(..., description="Translation status (pending/in_progress)")
    estimated_seconds: int | None = Field(
        None,
        description="Estimated time remaining in seconds"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chapter_slug": "chapter-1",
                    "language": "ur",
                    "status": "in_progress",
                    "estimated_seconds": 30
                }
            ]
        }
    }


class TranslationErrorResponse(BaseModel):
    """Translation error response."""

    chapter_slug: str = Field(..., description="Chapter identifier")
    language: str = Field(..., description="Target language code")
    status: str = Field(default="failed", description="Translation status")
    error_message: str = Field(..., description="Error message")

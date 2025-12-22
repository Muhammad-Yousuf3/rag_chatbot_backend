"""Authentication endpoint schemas.

Pydantic models for auth request/response validation.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    display_name: Optional[str] = Field(
        None, max_length=100, description="Display name"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserResponse" = Field(..., description="User information")

    model_config = {"json_schema_extra": {"examples": [{"access_token": "eyJ...", "token_type": "bearer", "user": {"id": "user_123", "email": "user@example.com", "display_name": "John Doe"}}]}}


class UserResponse(BaseModel):
    """User information response."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    display_name: Optional[str] = Field(None, description="Display name")
    experience_level: Optional[str] = Field(None, description="Experience level")
    preferred_language: Optional[str] = Field(None, description="Preferred language")
    chapters_read: Optional[List[str]] = Field(None, description="Chapters read")
    created_at: Optional[str] = Field(None, description="Account creation date")

    model_config = {"from_attributes": True, "json_schema_extra": {"examples": [{"id": "user_123", "email": "user@example.com", "display_name": "John Doe", "experience_level": "intermediate", "preferred_language": "en", "chapters_read": ["chapter-1", "chapter-2"]}]}}


class UserPreferencesUpdateRequest(BaseModel):
    """User preferences update request."""

    experience_level: Optional[str] = Field(
        None,
        description="Experience level (beginner/intermediate/advanced)",
    )
    preferred_language: Optional[str] = Field(
        None,
        description="Preferred language code",
    )

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate experience level value."""
        if v is None:
            return v
        valid_levels = {"beginner", "intermediate", "advanced"}
        if v not in valid_levels:
            raise ValueError(f"Invalid experience level. Must be one of: {valid_levels}")
        return v

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code."""
        if v is None:
            return v
        valid_languages = {"en", "ur"}
        if v not in valid_languages:
            raise ValueError(f"Invalid language. Must be one of: {valid_languages}")
        return v


class ConversationSummary(BaseModel):
    """Conversation summary for list view."""

    id: str = Field(..., description="Conversation ID")
    mode: str = Field(..., description="Conversation mode")
    message_count: int = Field(..., description="Number of messages")
    last_message_preview: Optional[str] = Field(None, description="Preview of last message")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class ConversationListResponse(BaseModel):
    """List of conversations response."""

    conversations: List[ConversationSummary] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")


class MessageResponse(BaseModel):
    """Message in conversation detail."""

    id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Message timestamp")


class ConversationDetailResponse(BaseModel):
    """Detailed conversation with messages."""

    id: str = Field(..., description="Conversation ID")
    user_id: Optional[str] = Field(None, description="Owner user ID")
    mode: str = Field(..., description="Conversation mode")
    selected_text: Optional[str] = Field(None, description="Selected text if applicable")
    messages: List[MessageResponse] = Field(..., description="Conversation messages")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# Update forward reference
TokenResponse.model_rebuild()

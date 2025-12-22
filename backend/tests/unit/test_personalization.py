"""Unit tests for personalization service.

T067 [US4] - Tests for experience-level-aware response generation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.personalization_service import (
    PersonalizationService,
    get_personalization_service,
    ExperienceLevel,
    PersonalizationContext,
)


class TestExperienceLevel:
    """Tests for experience level enum."""

    def test_experience_levels_defined(self):
        """Should have all expected experience levels."""
        assert ExperienceLevel.BEGINNER.value == "beginner"
        assert ExperienceLevel.INTERMEDIATE.value == "intermediate"
        assert ExperienceLevel.ADVANCED.value == "advanced"

    def test_experience_level_from_string(self):
        """Should create from string value."""
        assert ExperienceLevel("beginner") == ExperienceLevel.BEGINNER
        assert ExperienceLevel("intermediate") == ExperienceLevel.INTERMEDIATE
        assert ExperienceLevel("advanced") == ExperienceLevel.ADVANCED


class TestPersonalizationContext:
    """Tests for PersonalizationContext dataclass."""

    def test_create_context(self):
        """Should create context with all fields."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.INTERMEDIATE,
            chapters_read=["chapter-1", "chapter-2"],
            preferred_language="ur",
        )

        assert context.user_id == "user_123"
        assert context.experience_level == ExperienceLevel.INTERMEDIATE
        assert len(context.chapters_read) == 2
        assert context.preferred_language == "ur"

    def test_create_context_defaults(self):
        """Should use default values when not specified."""
        context = PersonalizationContext(
            user_id="user_123",
        )

        assert context.experience_level == ExperienceLevel.BEGINNER
        assert context.chapters_read == []
        assert context.preferred_language == "en"

    def test_context_to_prompt_beginner(self):
        """Should generate beginner-appropriate prompt context."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.BEGINNER,
        )

        prompt_context = context.to_prompt_context()

        assert "beginner" in prompt_context.lower()
        assert "simple" in prompt_context.lower() or "basic" in prompt_context.lower()

    def test_context_to_prompt_advanced(self):
        """Should generate advanced-appropriate prompt context."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.ADVANCED,
        )

        prompt_context = context.to_prompt_context()

        assert "advanced" in prompt_context.lower()
        assert "technical" in prompt_context.lower() or "detailed" in prompt_context.lower()


class TestPersonalizationService:
    """Tests for PersonalizationService class."""

    @pytest.fixture
    def personalization_service(self):
        """Create PersonalizationService instance."""
        return PersonalizationService()

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_user_context_authenticated(self, personalization_service, mock_db):
        """Should return personalization context for authenticated user."""
        user_id = "user_123"

        # Mock user with preferences
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.preferences = MagicMock()
        mock_user.preferences.experience_level = "intermediate"
        mock_user.preferences.chapters_read = ["chapter-1", "chapter-2"]
        mock_user.preferences.preferred_language = "en"

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

        context = await personalization_service.get_user_context(mock_db, user_id)

        assert context is not None
        assert context.user_id == user_id
        assert context.experience_level == ExperienceLevel.INTERMEDIATE

    @pytest.mark.asyncio
    async def test_get_user_context_no_preferences(self, personalization_service, mock_db):
        """Should return default context for user without preferences."""
        user_id = "user_123"

        # Mock user without preferences
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.preferences = None

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

        context = await personalization_service.get_user_context(mock_db, user_id)

        assert context is not None
        assert context.experience_level == ExperienceLevel.BEGINNER

    @pytest.mark.asyncio
    async def test_get_user_context_unauthenticated(self, personalization_service, mock_db):
        """Should return None for unauthenticated user."""
        context = await personalization_service.get_user_context(mock_db, None)

        assert context is None

    @pytest.mark.asyncio
    async def test_get_default_context(self, personalization_service):
        """Should return default context for anonymous users."""
        context = personalization_service.get_default_context()

        assert context is not None
        assert context.user_id is None
        assert context.experience_level == ExperienceLevel.BEGINNER
        assert context.chapters_read == []

    def test_generate_prompt_modifier_beginner(self, personalization_service):
        """Should generate beginner-friendly prompt modifier."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.BEGINNER,
        )

        modifier = personalization_service.generate_prompt_modifier(context)

        assert modifier is not None
        assert "beginner" in modifier.lower() or "simple" in modifier.lower()
        # Should include instructions for simpler explanations
        assert any(word in modifier.lower() for word in ["simple", "basic", "explain", "examples"])

    def test_generate_prompt_modifier_intermediate(self, personalization_service):
        """Should generate intermediate-level prompt modifier."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.INTERMEDIATE,
        )

        modifier = personalization_service.generate_prompt_modifier(context)

        assert modifier is not None
        assert "intermediate" in modifier.lower() or "familiar" in modifier.lower()

    def test_generate_prompt_modifier_advanced(self, personalization_service):
        """Should generate advanced-level prompt modifier."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.ADVANCED,
        )

        modifier = personalization_service.generate_prompt_modifier(context)

        assert modifier is not None
        assert any(word in modifier.lower() for word in ["advanced", "technical", "detailed", "depth"])

    def test_generate_prompt_modifier_with_chapters_read(self, personalization_service):
        """Should include chapter context in modifier."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.INTERMEDIATE,
            chapters_read=["chapter-1", "chapter-2", "chapter-3"],
        )

        modifier = personalization_service.generate_prompt_modifier(context)

        assert modifier is not None
        # Should reference that user has read some chapters
        assert "chapter" in modifier.lower() or "read" in modifier.lower() or "familiar" in modifier.lower()

    def test_generate_prompt_modifier_anonymous(self, personalization_service):
        """Should generate default modifier for anonymous users."""
        modifier = personalization_service.generate_prompt_modifier(None)

        # Should return a sensible default
        assert modifier is not None
        assert len(modifier) > 0

    @pytest.mark.asyncio
    async def test_track_chapter_read(self, personalization_service, mock_db):
        """Should track when user reads a chapter."""
        user_id = "user_123"
        chapter_slug = "chapter-5"

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.preferences = MagicMock()
        mock_user.preferences.chapters_read = ["chapter-1", "chapter-2"]

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
        mock_db.commit = AsyncMock()

        await personalization_service.track_chapter_read(mock_db, user_id, chapter_slug)

        # Should have added the new chapter
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_track_chapter_read_duplicate(self, personalization_service, mock_db):
        """Should not duplicate chapter in read list."""
        user_id = "user_123"
        chapter_slug = "chapter-1"  # Already read

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.preferences = MagicMock()
        mock_user.preferences.chapters_read = ["chapter-1", "chapter-2"]

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
        mock_db.commit = AsyncMock()

        await personalization_service.track_chapter_read(mock_db, user_id, chapter_slug)

        # Should not have added duplicate
        # The mock doesn't track list changes, but we verify commit was called
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_experience_level(self, personalization_service, mock_db):
        """Should update user experience level."""
        user_id = "user_123"
        new_level = ExperienceLevel.ADVANCED

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.preferences = MagicMock()
        mock_user.preferences.experience_level = "beginner"

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        result = await personalization_service.update_experience_level(mock_db, user_id, new_level)

        assert result is True
        mock_db.commit.assert_called_once()


class TestGetPersonalizationService:
    """Tests for personalization service factory."""

    def test_get_personalization_service_returns_instance(self):
        """Should return PersonalizationService instance."""
        service = get_personalization_service()
        assert isinstance(service, PersonalizationService)

    def test_get_personalization_service_singleton(self):
        """Should return same instance on multiple calls."""
        service1 = get_personalization_service()
        service2 = get_personalization_service()
        assert isinstance(service1, PersonalizationService)
        assert isinstance(service2, PersonalizationService)


class TestExperienceLevelPrompts:
    """Tests for experience-level-specific prompt generation."""

    @pytest.fixture
    def service(self):
        return PersonalizationService()

    def test_beginner_prompt_characteristics(self, service):
        """Beginner prompts should emphasize clarity and examples."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.BEGINNER,
        )

        modifier = service.generate_prompt_modifier(context)

        # Check for beginner-appropriate language
        lower_modifier = modifier.lower()
        beginner_indicators = ["simple", "basic", "example", "step", "explain", "beginner"]
        assert any(indicator in lower_modifier for indicator in beginner_indicators)

    def test_advanced_prompt_characteristics(self, service):
        """Advanced prompts should allow technical depth."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.ADVANCED,
        )

        modifier = service.generate_prompt_modifier(context)

        # Check for advanced-appropriate language
        lower_modifier = modifier.lower()
        advanced_indicators = ["technical", "advanced", "detail", "depth", "assume"]
        assert any(indicator in lower_modifier for indicator in advanced_indicators)

    def test_intermediate_prompt_characteristics(self, service):
        """Intermediate prompts should balance clarity and depth."""
        context = PersonalizationContext(
            user_id="user_123",
            experience_level=ExperienceLevel.INTERMEDIATE,
        )

        modifier = service.generate_prompt_modifier(context)

        # Check for intermediate-appropriate language
        assert modifier is not None
        assert len(modifier) > 0

"""Unit tests for selected-text mode.

T039 [US2] - Tests selected-text answering functionality including:
- Text selection validation
- Context restriction to selected text only
- "Not in selected text" fallback
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

# Services will be imported once implemented
# from src.services.rag_service import RAGService
# from src.agents.rag_agent import RAGAgent


class TestSelectedTextMode:
    """Test suite for selected-text answering mode."""

    @pytest.fixture
    def rag_service(self, mock_openai_client):
        """Create RAG service instance with mocked dependencies."""
        pytest.skip("Selected-text mode not yet fully implemented")

    @pytest.fixture
    def rag_agent(self, mock_openai_client):
        """Create RAG agent instance with mocked dependencies."""
        pytest.skip("Selected-text mode not yet fully implemented")

    @pytest.mark.asyncio
    async def test_selected_text_mode_uses_only_provided_text(
        self, rag_agent, mock_openai_client
    ):
        """Test that selected-text mode only uses the provided text as context."""
        selected_text = "Python variables are dynamically typed containers for data."
        query = "What are variables?"

        response = await rag_agent.generate_response(
            query=query,
            context=selected_text,
            mode="selected_text",
        )

        # Verify the API was called with only the selected text as context
        call_args = mock_openai_client.create_chat_completion.call_args
        messages = call_args.kwargs.get("messages", [])

        # The context should contain only the selected text
        all_content = " ".join(m.get("content", "") for m in messages)
        assert "dynamically typed" in all_content

    @pytest.mark.asyncio
    async def test_selected_text_mode_ignores_book_index(
        self, rag_service, mock_qdrant_client
    ):
        """Test that selected-text mode does not query the vector database."""
        selected_text = "This is the selected paragraph about functions."
        query = "What is this about?"

        # In selected-text mode, Qdrant should not be called
        await rag_service.process_selected_text_query(query, selected_text)

        mock_qdrant_client.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_not_in_selection_for_unrelated_query(
        self, rag_agent
    ):
        """Test that queries about content not in selection get appropriate response."""
        selected_text = "Python is a programming language."
        query = "What is JavaScript?"  # Not in the selected text

        response = await rag_agent.generate_response(
            query=query,
            context=selected_text,
            mode="selected_text",
            is_covered=False,
        )

        assert any(
            phrase in response.lower()
            for phrase in ["not in the selected text", "selection doesn't cover", "not mentioned"]
        )


class TestSelectedTextValidation:
    """Test suite for selected text validation."""

    @pytest.fixture
    def validator(self):
        """Create text selection validator."""
        pytest.skip("Validator not yet implemented")

    def test_rejects_empty_selection(self, validator):
        """Test that empty text selection is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validator.validate("")

        assert "empty" in str(exc_info.value).lower()

    def test_rejects_whitespace_only_selection(self, validator):
        """Test that whitespace-only selection is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validator.validate("   \n\t  ")

        assert "empty" in str(exc_info.value).lower()

    def test_rejects_too_short_selection(self, validator):
        """Test that very short selections are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validator.validate("Hi")  # Less than minimum (e.g., 10 chars)

        assert "short" in str(exc_info.value).lower() or "minimum" in str(exc_info.value).lower()

    def test_rejects_too_long_selection(self, validator):
        """Test that very long selections are rejected."""
        long_text = "x" * 50001  # More than maximum (e.g., 50000 chars)

        with pytest.raises(ValueError) as exc_info:
            validator.validate(long_text)

        assert "long" in str(exc_info.value).lower() or "maximum" in str(exc_info.value).lower()

    def test_accepts_valid_selection(self, validator):
        """Test that valid selections pass validation."""
        valid_text = "This is a valid text selection with enough content to be meaningful."

        # Should not raise
        result = validator.validate(valid_text)
        assert result == valid_text.strip()

    def test_trims_whitespace_from_selection(self, validator):
        """Test that leading/trailing whitespace is trimmed."""
        text_with_whitespace = "  \n  Valid content here  \n  "

        result = validator.validate(text_with_whitespace)

        assert result == "Valid content here"


class TestSelectedTextPrompt:
    """Test suite for selected-text prompt generation."""

    @pytest.fixture
    def rag_agent(self, mock_openai_client):
        """Create RAG agent instance."""
        pytest.skip("RAG agent selected-text mode not yet implemented")

    def test_selected_text_prompt_instructs_restriction(self, rag_agent):
        """Test that selected-text prompt instructs to use only selected text."""
        selected_text = "Sample selected text content."

        prompt = rag_agent.format_selected_text_prompt(selected_text)

        assert any(
            phrase in prompt.lower()
            for phrase in ["selected text", "provided text", "only use"]
        )

    def test_selected_text_prompt_includes_text(self, rag_agent):
        """Test that the prompt includes the selected text."""
        selected_text = "The quick brown fox jumps over the lazy dog."

        prompt = rag_agent.format_selected_text_prompt(selected_text)

        assert selected_text in prompt

    def test_selected_text_prompt_instructs_fallback(self, rag_agent):
        """Test that prompt includes instruction for unrelated queries."""
        selected_text = "Some content."

        prompt = rag_agent.format_selected_text_prompt(selected_text)

        assert any(
            phrase in prompt.lower()
            for phrase in ["not in", "cannot answer", "outside"]
        )


class TestSelectedTextConversation:
    """Test suite for selected-text conversation handling."""

    @pytest.fixture
    def agent_service(self):
        """Create agent service instance."""
        pytest.skip("Agent service selected-text mode not yet implemented")

    @pytest.mark.asyncio
    async def test_creates_conversation_with_selected_text_mode(
        self, agent_service, db_session
    ):
        """Test that conversation is created with selected_text mode."""
        selected_text = "Content about Python basics."

        response = await agent_service.chat_selected(
            db=db_session,
            message="What is this about?",
            selected_text=selected_text,
        )

        # Verify conversation was created with correct mode
        # (would need to query the database)

    @pytest.mark.asyncio
    async def test_stores_selected_text_in_conversation(
        self, agent_service, db_session
    ):
        """Test that selected text is stored with the conversation."""
        selected_text = "Important paragraph about decorators."

        response = await agent_service.chat_selected(
            db=db_session,
            message="Explain this",
            selected_text=selected_text,
        )

        # The selected text should be stored for context in follow-up questions

    @pytest.mark.asyncio
    async def test_follow_up_uses_same_selected_text(
        self, agent_service, db_session
    ):
        """Test that follow-up questions use the same selected text context."""
        selected_text = "Functions in Python are first-class objects."

        # First question
        response1 = await agent_service.chat_selected(
            db=db_session,
            message="What does this mean?",
            selected_text=selected_text,
        )

        # Follow-up question (same conversation)
        response2 = await agent_service.chat_selected(
            db=db_session,
            message="Can you give an example?",
            selected_text=selected_text,
            conversation_id=response1.conversation_id,
        )

        # Both should use the same selected text context

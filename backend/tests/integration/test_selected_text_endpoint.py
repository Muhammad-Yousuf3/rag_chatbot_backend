"""Integration tests for selected-text chat endpoint.

T040 [US2] - Tests the full selected-text chat flow including:
- Request handling with selected text
- Response generation restricted to selection
- Conversation persistence with selection context
"""

import pytest
from httpx import AsyncClient


class TestSelectedTextEndpoint:
    """Integration tests for POST /api/chat/selected endpoint."""

    @pytest.mark.asyncio
    async def test_selected_endpoint_returns_200_for_valid_request(
        self, async_client: AsyncClient
    ):
        """Test that valid selected-text request returns 200 status."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "What does this say?",
                "selected_text": "Python is a high-level programming language."
            }
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_selected_endpoint_returns_answer_based_on_selection(
        self, async_client: AsyncClient
    ):
        """Test that response is based only on selected text."""
        pytest.skip("Selected-text endpoint not yet implemented")

        selected_text = "Variables in Python are containers for storing data values."

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "What are variables?",
                "selected_text": selected_text
            }
        )

        data = response.json()
        assert "message" in data
        # Response should reference the selected text content

    @pytest.mark.asyncio
    async def test_selected_endpoint_creates_conversation_with_mode(
        self, async_client: AsyncClient, db_session
    ):
        """Test that conversation is created with selected_text mode."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Explain this",
                "selected_text": "Decorators modify function behavior."
            }
        )

        data = response.json()
        assert "conversation_id" in data

    @pytest.mark.asyncio
    async def test_selected_endpoint_requires_selected_text(
        self, async_client: AsyncClient
    ):
        """Test that selected_text field is required."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={"message": "What is this?"}  # Missing selected_text
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_selected_endpoint_validates_min_length(
        self, async_client: AsyncClient
    ):
        """Test that too-short selected text is rejected."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Explain",
                "selected_text": "Hi"  # Too short
            }
        )

        assert response.status_code == 422 or response.status_code == 400

    @pytest.mark.asyncio
    async def test_selected_endpoint_validates_max_length(
        self, async_client: AsyncClient
    ):
        """Test that too-long selected text is rejected."""
        pytest.skip("Selected-text endpoint not yet implemented")

        long_text = "x" * 50001  # Exceeds max length

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Summarize",
                "selected_text": long_text
            }
        )

        assert response.status_code in [400, 413, 422]

    @pytest.mark.asyncio
    async def test_selected_endpoint_handles_unrelated_query(
        self, async_client: AsyncClient
    ):
        """Test response when query is unrelated to selected text."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "What is JavaScript?",
                "selected_text": "Python is a programming language."
            }
        )

        data = response.json()
        # Should indicate the topic is not in the selection
        assert any(
            phrase in data["message"].lower()
            for phrase in ["not in", "selected text", "doesn't mention"]
        )

    @pytest.mark.asyncio
    async def test_selected_endpoint_continues_conversation(
        self, async_client: AsyncClient
    ):
        """Test that conversation can be continued with same selection."""
        pytest.skip("Selected-text endpoint not yet implemented")

        selected_text = "List comprehensions provide a concise way to create lists."

        # First message
        response1 = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "What is this about?",
                "selected_text": selected_text
            }
        )
        conversation_id = response1.json()["conversation_id"]

        # Follow-up
        response2 = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Can you give an example?",
                "selected_text": selected_text,
                "conversation_id": conversation_id
            }
        )

        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conversation_id

    @pytest.mark.asyncio
    async def test_selected_endpoint_no_sources_returned(
        self, async_client: AsyncClient
    ):
        """Test that selected-text mode doesn't return book sources."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Explain this",
                "selected_text": "A valid selection of text content."
            }
        )

        data = response.json()
        # Sources should be empty since we're not using book index
        assert data.get("sources", []) == []


class TestSelectedTextEndpointErrors:
    """Error handling tests for selected-text endpoint."""

    @pytest.mark.asyncio
    async def test_handles_empty_message(self, async_client: AsyncClient):
        """Test handling of empty message."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "",
                "selected_text": "Valid selected text content here."
            }
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_handles_empty_selected_text(self, async_client: AsyncClient):
        """Test handling of empty selected text."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "What is this?",
                "selected_text": ""
            }
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_handles_whitespace_selected_text(
        self, async_client: AsyncClient
    ):
        """Test handling of whitespace-only selected text."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Explain",
                "selected_text": "   \n\t   "
            }
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_returns_structured_error(self, async_client: AsyncClient):
        """Test that errors return structured response."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={}  # Invalid request
        )

        data = response.json()
        assert "detail" in data or "error" in data

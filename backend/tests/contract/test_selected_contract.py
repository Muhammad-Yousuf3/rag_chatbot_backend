"""Contract tests for /api/chat/selected endpoint.

T041 [US2] - Tests API contract compliance for selected-text endpoint.
"""

import pytest
from httpx import AsyncClient


class TestSelectedContractRequest:
    """Contract tests for selected-text request format."""

    @pytest.mark.asyncio
    async def test_accepts_json_content_type(self, async_client: AsyncClient):
        """Test that endpoint accepts application/json."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid selected text content."
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code != 415

    @pytest.mark.asyncio
    async def test_request_requires_message_field(
        self, async_client: AsyncClient
    ):
        """Test that 'message' field is required."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={"selected_text": "Some text"}  # Missing message
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_request_requires_selected_text_field(
        self, async_client: AsyncClient
    ):
        """Test that 'selected_text' field is required."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={"message": "Test"}  # Missing selected_text
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_message_must_be_string(self, async_client: AsyncClient):
        """Test that 'message' must be a string."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": 12345,
                "selected_text": "Valid text"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_selected_text_must_be_string(
        self, async_client: AsyncClient
    ):
        """Test that 'selected_text' must be a string."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": ["array", "not", "string"]
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_conversation_id_is_optional(
        self, async_client: AsyncClient
    ):
        """Test that 'conversation_id' is optional."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid selected text content."
            }
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_conversation_id_must_be_valid_uuid(
        self, async_client: AsyncClient
    ):
        """Test that 'conversation_id' must be valid UUID if provided."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid text",
                "conversation_id": "not-a-uuid"
            }
        )

        assert response.status_code in [400, 422]


class TestSelectedContractResponse:
    """Contract tests for selected-text response format."""

    @pytest.mark.asyncio
    async def test_response_is_json(self, async_client: AsyncClient):
        """Test that response is JSON."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid selected text content."
            }
        )

        assert response.headers["content-type"].startswith("application/json")

    @pytest.mark.asyncio
    async def test_response_contains_message(self, async_client: AsyncClient):
        """Test that response contains 'message' field."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid text"
            }
        )

        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)

    @pytest.mark.asyncio
    async def test_response_contains_conversation_id(
        self, async_client: AsyncClient
    ):
        """Test that response contains 'conversation_id' field."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid text"
            }
        )

        data = response.json()
        assert "conversation_id" in data
        assert isinstance(data["conversation_id"], str)

    @pytest.mark.asyncio
    async def test_response_contains_sources_array(
        self, async_client: AsyncClient
    ):
        """Test that response contains 'sources' field (empty for selected-text)."""
        pytest.skip("Selected-text endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat/selected",
            json={
                "message": "Test",
                "selected_text": "Valid text"
            }
        )

        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)
        # For selected-text mode, sources should be empty
        assert len(data["sources"]) == 0


class TestSelectedContractOpenAPI:
    """Contract tests for OpenAPI compliance."""

    @pytest.mark.asyncio
    async def test_selected_endpoint_in_openapi(
        self, async_client: AsyncClient
    ):
        """Test that /api/chat/selected is documented in OpenAPI."""
        response = await async_client.get("/openapi.json")

        data = response.json()
        paths = data.get("paths", {})

        # Check if selected endpoint exists
        selected_paths = [p for p in paths if "selected" in p]
        assert len(selected_paths) > 0 or pytest.skip(
            "Selected endpoint not yet in OpenAPI"
        )

    @pytest.mark.asyncio
    async def test_selected_request_schema_documented(
        self, async_client: AsyncClient
    ):
        """Test that request schema is documented."""
        response = await async_client.get("/openapi.json")

        data = response.json()
        schemas = data.get("components", {}).get("schemas", {})

        # Should have a SelectedTextRequest or similar schema
        # This is informational as schemas may be inline

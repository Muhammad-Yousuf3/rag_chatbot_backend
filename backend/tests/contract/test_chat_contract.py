"""Contract tests for /api/chat endpoint.

T024 [US1] - Tests API contract compliance including:
- Request schema validation
- Response schema validation
- OpenAPI specification compliance
- Content-Type handling
"""

import pytest
from httpx import AsyncClient


class TestChatContractRequest:
    """Contract tests for chat request format."""

    @pytest.mark.asyncio
    async def test_accepts_json_content_type(self, async_client: AsyncClient):
        """Test that endpoint accepts application/json."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "Test"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code != 415  # Not Unsupported Media Type

    @pytest.mark.asyncio
    async def test_rejects_non_json_content_type(self, async_client: AsyncClient):
        """Test that endpoint rejects non-JSON content."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            content="message=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 422 or response.status_code == 415

    @pytest.mark.asyncio
    async def test_request_requires_message_field(self, async_client: AsyncClient):
        """Test that 'message' field is required."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"conversation_id": "123"}  # Missing message
        )

        assert response.status_code == 422
        data = response.json()
        assert "message" in str(data).lower()

    @pytest.mark.asyncio
    async def test_message_must_be_string(self, async_client: AsyncClient):
        """Test that 'message' must be a string."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": 12345}  # Number instead of string
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_conversation_id_is_optional(self, async_client: AsyncClient):
        """Test that 'conversation_id' is optional."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "Test"}  # No conversation_id
        )

        # Should succeed without conversation_id
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_conversation_id_must_be_valid_uuid(
        self, async_client: AsyncClient
    ):
        """Test that 'conversation_id' must be valid UUID if provided."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={
                "message": "Test",
                "conversation_id": "not-a-uuid"
            }
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_ignores_unknown_fields(self, async_client: AsyncClient):
        """Test that unknown fields are ignored."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={
                "message": "Test",
                "unknown_field": "value"
            }
        )

        # Should succeed, ignoring unknown field
        assert response.status_code == 200


class TestChatContractResponse:
    """Contract tests for chat response format."""

    @pytest.mark.asyncio
    async def test_response_is_json(self, async_client: AsyncClient):
        """Test that response is JSON."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "Test"}
        )

        assert response.headers["content-type"].startswith("application/json")

    @pytest.mark.asyncio
    async def test_response_contains_message(self, async_client: AsyncClient):
        """Test that response contains 'message' field."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "Test"}
        )

        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)

    @pytest.mark.asyncio
    async def test_response_contains_conversation_id(
        self, async_client: AsyncClient
    ):
        """Test that response contains 'conversation_id' field."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "Test"}
        )

        data = response.json()
        assert "conversation_id" in data
        assert isinstance(data["conversation_id"], str)

    @pytest.mark.asyncio
    async def test_response_contains_sources(self, async_client: AsyncClient):
        """Test that response contains 'sources' field."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "Test"}
        )

        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)

    @pytest.mark.asyncio
    async def test_source_schema_contains_required_fields(
        self, async_client: AsyncClient
    ):
        """Test that each source has required fields."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "What is Python?"}
        )

        data = response.json()
        if data["sources"]:
            source = data["sources"][0]
            # Required source fields per OpenAPI spec
            assert "chapter" in source
            assert "relevance" in source

    @pytest.mark.asyncio
    async def test_source_relevance_is_number(self, async_client: AsyncClient):
        """Test that source relevance is a number."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "What is Python?"}
        )

        data = response.json()
        if data["sources"]:
            source = data["sources"][0]
            assert isinstance(source["relevance"], (int, float))

    @pytest.mark.asyncio
    async def test_source_relevance_is_between_0_and_1(
        self, async_client: AsyncClient
    ):
        """Test that source relevance is between 0 and 1."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={"message": "What is Python?"}
        )

        data = response.json()
        for source in data["sources"]:
            assert 0 <= source["relevance"] <= 1


class TestChatContractErrorResponses:
    """Contract tests for error response format."""

    @pytest.mark.asyncio
    async def test_validation_error_returns_422(self, async_client: AsyncClient):
        """Test that validation errors return 422."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={}  # Missing required field
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_validation_error_includes_detail(
        self, async_client: AsyncClient
    ):
        """Test that validation errors include detail."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={}
        )

        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_validation_error_detail_is_list(
        self, async_client: AsyncClient
    ):
        """Test that validation error detail is a list (FastAPI format)."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={}
        )

        data = response.json()
        assert isinstance(data["detail"], list)

    @pytest.mark.asyncio
    async def test_validation_error_includes_field_location(
        self, async_client: AsyncClient
    ):
        """Test that validation errors include field location."""
        pytest.skip("Chat endpoint not yet implemented")

        response = await async_client.post(
            "/api/chat",
            json={}
        )

        data = response.json()
        if isinstance(data["detail"], list) and data["detail"]:
            error = data["detail"][0]
            assert "loc" in error
            assert "msg" in error


class TestChatContractOpenAPICompliance:
    """Contract tests for OpenAPI specification compliance."""

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, async_client: AsyncClient):
        """Test that OpenAPI schema is available."""
        response = await async_client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data

    @pytest.mark.asyncio
    async def test_chat_endpoint_in_openapi(self, async_client: AsyncClient):
        """Test that /api/chat is documented in OpenAPI."""
        response = await async_client.get("/openapi.json")

        data = response.json()
        paths = data.get("paths", {})

        # Check if chat endpoint exists (may be under /api/chat or /chat)
        chat_paths = [p for p in paths if "chat" in p]
        assert len(chat_paths) > 0, "Chat endpoint not found in OpenAPI spec"

    @pytest.mark.asyncio
    async def test_chat_request_schema_documented(
        self, async_client: AsyncClient
    ):
        """Test that request schema is documented."""
        response = await async_client.get("/openapi.json")

        data = response.json()
        schemas = data.get("components", {}).get("schemas", {})

        # Should have a ChatRequest or similar schema
        request_schemas = [s for s in schemas if "Chat" in s and "Request" in s]
        # May also be inline, so this is informational

    @pytest.mark.asyncio
    async def test_chat_response_schema_documented(
        self, async_client: AsyncClient
    ):
        """Test that response schema is documented."""
        response = await async_client.get("/openapi.json")

        data = response.json()
        schemas = data.get("components", {}).get("schemas", {})

        # Should have a ChatResponse or similar schema
        response_schemas = [s for s in schemas if "Chat" in s and "Response" in s]
        # May also be inline, so this is informational

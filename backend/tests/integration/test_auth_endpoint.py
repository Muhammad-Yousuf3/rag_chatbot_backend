"""Integration tests for authentication endpoints.

T068 [US4] - Tests for /api/auth endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


class TestAuthEndpoints:
    """Integration tests for auth API endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_auth_service(self):
        """Create mock auth service."""
        service = MagicMock()
        service.register_user = AsyncMock()
        service.authenticate_user = AsyncMock()
        service.create_access_token = MagicMock(return_value="mock_token_123")
        service.verify_token = MagicMock()
        service.get_user_by_id = AsyncMock()
        service.update_user_preferences = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_db, mock_auth_service):
        """Should register new user and return token."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        # Mock new user
        mock_user = MagicMock()
        mock_user.id = "new_user_id"
        mock_user.email = "newuser@example.com"
        mock_user.display_name = "New User"
        mock_user.created_at = "2024-01-15T10:00:00Z"
        mock_auth_service.register_user.return_value = mock_user

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/auth/register",
                    json={
                        "email": "newuser@example.com",
                        "password": "secure_password_123",
                        "display_name": "New User",
                    },
                )

            assert response.status_code == 201
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == "newuser@example.com"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, mock_db, mock_auth_service):
        """Should return 400 for duplicate email."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_auth_service.register_user.side_effect = ValueError("Email already registered")

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/auth/register",
                    json={
                        "email": "existing@example.com",
                        "password": "password123",
                    },
                )

            assert response.status_code == 400
            assert "already registered" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, mock_db, mock_auth_service):
        """Should return 400 for weak password."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/auth/register",
                    json={
                        "email": "user@example.com",
                        "password": "123",  # Too short
                    },
                )

            # Pydantic validation should catch this
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_success(self, mock_db, mock_auth_service):
        """Should login user and return token."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_user.email = "user@example.com"
        mock_user.display_name = "Test User"
        mock_auth_service.authenticate_user.return_value = mock_user

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/auth/login",
                    json={
                        "email": "user@example.com",
                        "password": "correct_password",
                    },
                )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_db, mock_auth_service):
        """Should return 401 for invalid credentials."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_auth_service.authenticate_user.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/auth/login",
                    json={
                        "email": "user@example.com",
                        "password": "wrong_password",
                    },
                )

            assert response.status_code == 401
            assert "invalid" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_current_user_authenticated(self, mock_db, mock_auth_service):
        """Should return current user for valid token."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service, TokenData

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_user.email = "user@example.com"
        mock_user.display_name = "Test User"
        mock_user.experience_level = "intermediate"
        mock_user.created_at = "2024-01-15T10:00:00Z"

        mock_auth_service.verify_token.return_value = TokenData(
            user_id="user_123",
            email="user@example.com",
        )
        mock_auth_service.get_user_by_id.return_value = mock_user

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/auth/me",
                    headers={"Authorization": "Bearer valid_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "user@example.com"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_current_user_unauthenticated(self, mock_db, mock_auth_service):
        """Should return 401 for missing/invalid token."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_auth_service.verify_token.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/auth/me")

            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_preferences_success(self, mock_db, mock_auth_service):
        """Should update user preferences."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service, TokenData

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_user.email = "user@example.com"
        mock_user.preferences = MagicMock()
        mock_user.preferences.experience_level = "advanced"
        mock_user.preferences.preferred_language = "ur"

        mock_auth_service.verify_token.return_value = TokenData(
            user_id="user_123",
            email="user@example.com",
        )
        mock_auth_service.get_user_by_id.return_value = mock_user
        mock_auth_service.update_user_preferences.return_value = mock_user

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/auth/preferences",
                    headers={"Authorization": "Bearer valid_token"},
                    json={
                        "experience_level": "advanced",
                        "preferred_language": "ur",
                    },
                )

            assert response.status_code == 200
            mock_auth_service.update_user_preferences.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_experience_level(self, mock_db, mock_auth_service):
        """Should return 400 for invalid experience level."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service, TokenData

        mock_auth_service.verify_token.return_value = TokenData(
            user_id="user_123",
            email="user@example.com",
        )

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/auth/preferences",
                    headers={"Authorization": "Bearer valid_token"},
                    json={
                        "experience_level": "invalid_level",
                    },
                )

            # Should be validation error
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


class TestConversationHistoryEndpoints:
    """Integration tests for conversation history endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_auth_service(self):
        """Create mock auth service."""
        from src.services.auth_service import TokenData

        service = MagicMock()
        service.verify_token = MagicMock(return_value=TokenData(
            user_id="user_123",
            email="user@example.com",
        ))
        service.get_user_by_id = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_conversations_authenticated(self, mock_db, mock_auth_service):
        """Should return user's conversation history."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_auth_service.get_user_by_id.return_value = mock_user

        # Mock conversations
        mock_conversations = [
            MagicMock(
                id="conv_1",
                user_id="user_123",
                created_at="2024-01-15T10:00:00Z",
                updated_at="2024-01-15T10:30:00Z",
            ),
            MagicMock(
                id="conv_2",
                user_id="user_123",
                created_at="2024-01-14T09:00:00Z",
                updated_at="2024-01-14T09:45:00Z",
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_conversations
        mock_db.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/chat/conversations",
                    headers={"Authorization": "Bearer valid_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "conversations" in data
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_conversations_unauthenticated(self, mock_db, mock_auth_service):
        """Should return 401 for unauthenticated request."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_auth_service.verify_token.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/chat/conversations")

            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self, mock_db, mock_auth_service):
        """Should return specific conversation with messages."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_auth_service.get_user_by_id.return_value = mock_user

        # Mock conversation with messages
        mock_conversation = MagicMock()
        mock_conversation.id = "conv_1"
        mock_conversation.user_id = "user_123"
        mock_conversation.messages = [
            MagicMock(
                id="msg_1",
                role="user",
                content="Hello",
                created_at="2024-01-15T10:00:00Z",
            ),
            MagicMock(
                id="msg_2",
                role="assistant",
                content="Hi! How can I help?",
                created_at="2024-01-15T10:00:05Z",
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_conversation
        mock_db.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/chat/conversations/conv_1",
                    headers={"Authorization": "Bearer valid_token"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "conv_1"
            assert "messages" in data
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, mock_db, mock_auth_service):
        """Should return 404 for non-existent conversation."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_auth_service.get_user_by_id.return_value = mock_user

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/chat/conversations/nonexistent",
                    headers={"Authorization": "Bearer valid_token"},
                )

            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_conversation_wrong_user(self, mock_db, mock_auth_service):
        """Should return 404 for conversation belonging to another user."""
        from src.main import app
        from src.db.database import get_db
        from src.services.auth_service import get_auth_service

        mock_user = MagicMock()
        mock_user.id = "user_123"
        mock_auth_service.get_user_by_id.return_value = mock_user

        # Conversation belongs to different user
        mock_conversation = MagicMock()
        mock_conversation.id = "conv_1"
        mock_conversation.user_id = "other_user"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_conversation
        mock_db.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/chat/conversations/conv_1",
                    headers={"Authorization": "Bearer valid_token"},
                )

            # Should return 404 to not reveal existence of other users' conversations
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

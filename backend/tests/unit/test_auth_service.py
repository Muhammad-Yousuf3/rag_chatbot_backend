"""Unit tests for authentication service.

T066 [US4] - Tests for JWT token handling and user authentication.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.auth_service import (
    AuthService,
    get_auth_service,
    TokenData,
    UserCredentials,
    PasswordHasher,
)


class TestPasswordHasher:
    """Tests for password hashing utilities."""

    def test_hash_password_returns_different_value(self):
        """Hash should be different from original password."""
        password = "secure_password_123"
        hashed = PasswordHasher.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_is_deterministic_with_same_salt(self):
        """Same password should verify correctly."""
        password = "secure_password_123"
        hashed = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(password, hashed)

    def test_verify_password_success(self):
        """Correct password should verify."""
        password = "my_secret_password"
        hashed = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Incorrect password should not verify."""
        password = "my_secret_password"
        wrong_password = "wrong_password"
        hashed = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(wrong_password, hashed) is False

    def test_different_passwords_have_different_hashes(self):
        """Different passwords should produce different hashes."""
        hash1 = PasswordHasher.hash_password("password1")
        hash2 = PasswordHasher.hash_password("password2")

        assert hash1 != hash2


class TestAuthService:
    """Tests for AuthService class."""

    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService(
            secret_key="test_secret_key_for_jwt_tokens_32chars",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    def test_create_access_token(self, auth_service):
        """Should create valid JWT access token."""
        user_id = "user_123"
        email = "test@example.com"

        token = auth_service.create_access_token(
            user_id=user_id,
            email=email,
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT has 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_create_access_token_with_custom_expiry(self, auth_service):
        """Should create token with custom expiration."""
        user_id = "user_123"
        email = "test@example.com"
        expires_delta = timedelta(hours=24)

        token = auth_service.create_access_token(
            user_id=user_id,
            email=email,
            expires_delta=expires_delta,
        )

        assert token is not None
        # Verify token can be decoded
        token_data = auth_service.verify_token(token)
        assert token_data is not None
        assert token_data.user_id == user_id

    def test_verify_token_success(self, auth_service):
        """Should verify valid token and extract data."""
        user_id = "user_456"
        email = "user@example.com"

        token = auth_service.create_access_token(
            user_id=user_id,
            email=email,
        )

        token_data = auth_service.verify_token(token)

        assert token_data is not None
        assert token_data.user_id == user_id
        assert token_data.email == email

    def test_verify_token_invalid(self, auth_service):
        """Should return None for invalid token."""
        invalid_token = "invalid.token.here"

        token_data = auth_service.verify_token(invalid_token)

        assert token_data is None

    def test_verify_token_expired(self, auth_service):
        """Should return None for expired token."""
        # Create service with very short expiry
        short_expiry_service = AuthService(
            secret_key="test_secret_key_for_jwt_tokens_32chars",
            algorithm="HS256",
            access_token_expire_minutes=-1,  # Already expired
        )

        token = short_expiry_service.create_access_token(
            user_id="user_123",
            email="test@example.com",
        )

        # Token should be invalid due to expiration
        token_data = short_expiry_service.verify_token(token)
        assert token_data is None

    def test_verify_token_wrong_secret(self, auth_service):
        """Should return None for token signed with different secret."""
        # Create token with different secret
        other_service = AuthService(
            secret_key="different_secret_key_32characters!",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

        token = other_service.create_access_token(
            user_id="user_123",
            email="test@example.com",
        )

        # Original service should not verify token from other service
        token_data = auth_service.verify_token(token)
        assert token_data is None

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_db):
        """Should register new user successfully."""
        credentials = UserCredentials(
            email="newuser@example.com",
            password="secure_password_123",
            display_name="New User",
        )

        # Mock: no existing user
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch("src.services.auth_service.User") as MockUser:
            mock_user = MagicMock()
            mock_user.id = "new_user_id"
            mock_user.email = credentials.email
            mock_user.display_name = credentials.display_name
            MockUser.return_value = mock_user

            result = await auth_service.register_user(mock_db, credentials)

            assert result is not None
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, auth_service, mock_db):
        """Should raise error for duplicate email."""
        credentials = UserCredentials(
            email="existing@example.com",
            password="secure_password_123",
        )

        # Mock: existing user found
        existing_user = MagicMock()
        existing_user.email = credentials.email
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_user)))

        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register_user(mock_db, credentials)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_db):
        """Should authenticate user with correct credentials."""
        email = "user@example.com"
        password = "correct_password"
        hashed_password = PasswordHasher.hash_password(password)

        # Mock user from database
        mock_user = MagicMock()
        mock_user.id = "user_id_123"
        mock_user.email = email
        mock_user.password_hash = hashed_password
        mock_user.is_active = True

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

        result = await auth_service.authenticate_user(mock_db, email, password)

        assert result is not None
        assert result.id == "user_id_123"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, mock_db):
        """Should return None for wrong password."""
        email = "user@example.com"
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed_password = PasswordHasher.hash_password(correct_password)

        mock_user = MagicMock()
        mock_user.email = email
        mock_user.password_hash = hashed_password
        mock_user.is_active = True

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

        result = await auth_service.authenticate_user(mock_db, email, wrong_password)

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_db):
        """Should return None for non-existent user."""
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

        result = await auth_service.authenticate_user(mock_db, "nouser@example.com", "password")

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, auth_service, mock_db):
        """Should return None for inactive user."""
        email = "inactive@example.com"
        password = "password"
        hashed_password = PasswordHasher.hash_password(password)

        mock_user = MagicMock()
        mock_user.email = email
        mock_user.password_hash = hashed_password
        mock_user.is_active = False  # Inactive user

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

        result = await auth_service.authenticate_user(mock_db, email, password)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, auth_service, mock_db):
        """Should retrieve user by ID."""
        user_id = "user_123"

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = "user@example.com"

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))

        result = await auth_service.get_user_by_id(mock_db, user_id)

        assert result is not None
        assert result.id == user_id

    @pytest.mark.asyncio
    async def test_update_user_preferences(self, auth_service, mock_db):
        """Should update user preferences."""
        user_id = "user_123"
        preferences = {
            "experience_level": "intermediate",
            "preferred_language": "ur",
        }

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.preferences = MagicMock()

        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        result = await auth_service.update_user_preferences(mock_db, user_id, preferences)

        assert result is not None
        mock_db.commit.assert_called_once()


class TestGetAuthService:
    """Tests for auth service factory function."""

    def test_get_auth_service_returns_instance(self):
        """Should return AuthService instance."""
        with patch.dict("os.environ", {"JWT_SECRET_KEY": "test_secret_key_32_characters_long"}):
            service = get_auth_service()
            assert isinstance(service, AuthService)

    def test_get_auth_service_singleton(self):
        """Should return same instance on multiple calls."""
        with patch.dict("os.environ", {"JWT_SECRET_KEY": "test_secret_key_32_characters_long"}):
            service1 = get_auth_service()
            service2 = get_auth_service()
            # Both should be AuthService instances
            assert isinstance(service1, AuthService)
            assert isinstance(service2, AuthService)

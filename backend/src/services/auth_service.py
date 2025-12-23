"""Authentication service with JWT handling.

T072 [US4] - Implements user registration, login, and token management.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.user import User, UserPreference, ExperienceLevel


@dataclass
class TokenData:
    """JWT token payload data."""

    user_id: str
    email: str
    exp: Optional[datetime] = None


@dataclass
class UserCredentials:
    """User registration/login credentials."""

    email: str
    password: str
    display_name: Optional[str] = None


class PasswordHasher:
    """Password hashing utilities using bcrypt."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password.

        Returns:
            Hashed password string.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password.
            hashed_password: Stored hashed password.

        Returns:
            True if password matches, False otherwise.
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False


class AuthService:
    """Service for user authentication and JWT token management."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        """Initialize auth service.

        Args:
            secret_key: Secret key for JWT signing.
            algorithm: JWT algorithm (default HS256).
            access_token_expire_minutes: Token expiration time in minutes.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token.

        Args:
            user_id: User ID to encode.
            email: User email to encode.
            expires_delta: Optional custom expiration time.

        Returns:
            JWT token string.
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
        }

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token.

        Args:
            token: JWT token string.

        Returns:
            TokenData if valid, None otherwise.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            user_id = payload.get("sub")
            email = payload.get("email")

            if user_id is None or email is None:
                return None

            return TokenData(
                user_id=user_id,
                email=email,
                exp=payload.get("exp"),
            )
        except JWTError:
            return None

    async def register_user(
        self,
        db: AsyncSession,
        credentials: UserCredentials,
    ) -> User:
        """Register a new user.

        Args:
            db: Database session.
            credentials: User credentials.

        Returns:
            Created user object.

        Raises:
            ValueError: If email already registered.
        """
        # Check for existing user
        stmt = select(User).where(User.email == credentials.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user_id = str(uuid4())
        user = User(
            id=user_id,
            email=credentials.email,
            password_hash=PasswordHasher.hash_password(credentials.password),
            display_name=credentials.display_name,
            is_active=True,
        )

        # Create default preferences
        preferences = UserPreference(
            id=str(uuid4()),
            user_id=user_id,
            experience_level=ExperienceLevel.BEGINNER,
            preferred_language="en",
            chapters_read=[],
        )

        db.add(user)
        db.add(preferences)
        await db.commit()
        await db.refresh(user)

        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with email and password.

        Args:
            db: Database session.
            email: User email.
            password: Plain text password.

        Returns:
            User if authenticated, None otherwise.
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.is_active:
            return None

        if not PasswordHasher.verify_password(password, user.password_hash):
            return None

        return user

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[User]:
        """Get user by ID with preferences.

        Args:
            db: Database session.
            user_id: User ID.

        Returns:
            User if found, None otherwise.
        """
        stmt = (
            select(User)
            .options(selectinload(User.preferences))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        """Get user by email.

        Args:
            db: Database session.
            email: User email.

        Returns:
            User if found, None otherwise.
        """
        stmt = (
            select(User)
            .options(selectinload(User.preferences))
            .where(User.email == email)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_preferences(
        self,
        db: AsyncSession,
        user_id: str,
        preferences: dict,
    ) -> Optional[User]:
        """Update user preferences.

        Args:
            db: Database session.
            user_id: User ID.
            preferences: Preference updates.

        Returns:
            Updated user, or None if not found.
        """
        stmt = (
            select(User)
            .options(selectinload(User.preferences))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.preferences:
            # Create preferences if not exist
            user.preferences = UserPreference(
                id=str(uuid4()),
                user_id=user_id,
            )
            db.add(user.preferences)

        # Update fields
        if "experience_level" in preferences:
            user.preferences.experience_level = ExperienceLevel(
                preferences["experience_level"]
            )

        if "preferred_language" in preferences:
            user.preferences.preferred_language = preferences["preferred_language"]

        if "chapters_read" in preferences:
            user.preferences.chapters_read = preferences["chapters_read"]

        if "custom_settings" in preferences:
            user.preferences.custom_settings = preferences["custom_settings"]

        await db.commit()
        await db.refresh(user)

        return user


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create AuthService singleton.

    Returns:
        AuthService instance.
    """
    global _auth_service

    if _auth_service is None:
        secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        _auth_service = AuthService(
            secret_key=secret_key,
            algorithm=algorithm,
            access_token_expire_minutes=expire_minutes,
        )

    return _auth_service

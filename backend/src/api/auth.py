"""Authentication API endpoints.

T073-T076 [US4] - Implements /api/auth endpoints for registration, login, and preferences.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserPreferencesUpdateRequest,
    UserRegisterRequest,
    UserResponse,
)
from ..services.auth_service import (
    AuthService,
    UserCredentials,
    get_auth_service,
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[dict]:
    """Get current user if authenticated (optional).

    Args:
        credentials: Bearer token credentials.
        db: Database session.
        auth_service: Auth service.

    Returns:
        User dict if authenticated, None otherwise.
    """
    if not credentials:
        return None

    token_data = auth_service.verify_token(credentials.credentials)
    if not token_data:
        return None

    user = await auth_service.get_user_by_id(db, token_data.user_id)
    if not user:
        return None

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "preferences": user.preferences,
    }


async def get_current_user_required(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Get current user (required).

    Args:
        credentials: Bearer token credentials.
        db: Database session.
        auth_service: Auth service.

    Returns:
        User dict.

    Raises:
        HTTPException: If not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = auth_service.verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "preferences": user.preferences,
    }


def _user_to_response(user, include_preferences: bool = True) -> UserResponse:
    """Convert user model to response.

    Args:
        user: User model or dict.
        include_preferences: Whether to include preferences.

    Returns:
        UserResponse object.
    """
    if isinstance(user, dict):
        preferences = user.get("preferences")
        return UserResponse(
            id=user["id"],
            email=user["email"],
            display_name=user.get("display_name"),
            experience_level=preferences.experience_level.value if preferences else None,
            preferred_language=preferences.preferred_language if preferences else None,
            chapters_read=preferences.chapters_read if preferences else None,
            created_at=None,
        )

    preferences = user.preferences if include_preferences else None
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        experience_level=preferences.experience_level.value if preferences else None,
        preferred_language=preferences.preferred_language if preferences else None,
        chapters_read=preferences.chapters_read if preferences else None,
        created_at=str(user.created_at) if user.created_at else None,
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return access token.",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email already registered or invalid data"},
    },
)
async def register_user(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user.

    Args:
        request: Registration request.
        db: Database session.
        auth_service: Auth service.

    Returns:
        Token response with user info.
    """
    try:
        credentials = UserCredentials(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )

        user = await auth_service.register_user(db, credentials)

        # Create access token
        access_token = auth_service.create_access_token(
            user_id=user.id,
            email=user.email,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=_user_to_response(user),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access token.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login_user(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate user and return token.

    Args:
        request: Login request.
        db: Database session.
        auth_service: Auth service.

    Returns:
        Token response with user info.
    """
    user = await auth_service.authenticate_user(
        db,
        request.email,
        request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reload user with preferences
    user = await auth_service.get_user_by_id(db, user.id)

    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_user_to_response(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information.",
    responses={
        200: {"description": "User information"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user(
    current_user: dict = Depends(get_current_user_required),
):
    """Get current user information.

    Args:
        current_user: Authenticated user.

    Returns:
        User information.
    """
    return _user_to_response(current_user)


@router.put(
    "/preferences",
    response_model=UserResponse,
    summary="Update user preferences",
    description="Update the current user's preferences.",
    responses={
        200: {"description": "Preferences updated"},
        401: {"description": "Not authenticated"},
    },
)
async def update_preferences(
    request: UserPreferencesUpdateRequest,
    current_user: dict = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update user preferences.

    Args:
        request: Preferences update request.
        current_user: Authenticated user.
        db: Database session.
        auth_service: Auth service.

    Returns:
        Updated user information.
    """
    preferences_update = {}

    if request.experience_level is not None:
        preferences_update["experience_level"] = request.experience_level

    if request.preferred_language is not None:
        preferences_update["preferred_language"] = request.preferred_language

    if preferences_update:
        user = await auth_service.update_user_preferences(
            db,
            current_user["id"],
            preferences_update,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return _user_to_response(user)

    # No updates, return current user
    user = await auth_service.get_user_by_id(db, current_user["id"])
    return _user_to_response(user)

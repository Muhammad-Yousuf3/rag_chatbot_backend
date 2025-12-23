"""API router initialization."""

from fastapi import APIRouter

from .auth import router as auth_router
from .chat import router as chat_router
from .health import router as health_router
from .translate import router as translate_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(translate_router)

"""API router initialization."""

from fastapi import APIRouter

from src.api.auth import router as auth_router
from src.api.chat import router as chat_router
from src.api.health import router as health_router
from src.api.translate import router as translate_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(translate_router)

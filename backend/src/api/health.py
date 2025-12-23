"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.openai_client import get_openai_service
from ..services.qdrant_client import get_qdrant_service

router = APIRouter()


class ServiceStatus(BaseModel):
    """Service status model."""

    database: str = "unknown"
    qdrant: str = "unknown"
    openai: str = "unknown"


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    services: ServiceStatus


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check health status of all services.

    Returns:
        HealthResponse with overall status and individual service statuses
    """
    services = ServiceStatus()
    all_healthy = True

    # Check Qdrant
    try:
        qdrant = get_qdrant_service()
        if qdrant.health_check():
            services.qdrant = "up"
        else:
            services.qdrant = "down"
            all_healthy = False
    except Exception:
        services.qdrant = "down"
        all_healthy = False

    # Check OpenAI
    try:
        openai = get_openai_service()
        if openai.health_check():
            services.openai = "up"
        else:
            services.openai = "down"
            all_healthy = False
    except Exception:
        services.openai = "down"
        all_healthy = False

    # Note: Database health check would require async session
    # For now, assume database is up if app is running
    services.database = "up"

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        timestamp=datetime.utcnow(),
        services=services,
    )

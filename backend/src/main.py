"""FastAPI application entry point.

T086 - Enhanced with comprehensive error handling.
T088 - Integrates rate limiting middleware.
T089 - Integrates structured logging.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.api import router as api_router
from backend.src.config import get_settings
from backend.src.middleware.rate_limit import RateLimitMiddleware, RateLimitConfig
from backend.src.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    settings = get_settings()
    setup_logging(level=settings.log_level)
    logger.info("Starting RAG Chatbot API", environment=settings.environment)
    yield
    # Shutdown
    logger.info("Shutting down RAG Chatbot API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="RAG Chatbot API",
        description="Book-grounded RAG chatbot with personalization and translation",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add rate limiting middleware
    rate_limit_config = RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        burst_size=10,
    )
    app.add_middleware(
        RateLimitMiddleware,
        config=rate_limit_config,
        exclude_paths=["/api/health", "/docs", "/redoc", "/openapi.json"],
    )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions."""
        logger.error(
            "Unhandled exception",
            error=str(exc),
            path=str(request.url),
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred. Please try again later.",
                "error_code": "INTERNAL_ERROR",
            },
        )

    # Include API router
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8080))

    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=port, reload=False)




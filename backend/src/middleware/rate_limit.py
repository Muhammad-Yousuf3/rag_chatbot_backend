"""Rate limiting middleware.

T088 - Implements rate limiting for API endpoints.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10


@dataclass
class ClientRateInfo:
    """Rate tracking information for a client."""

    minute_requests: list = field(default_factory=list)
    hour_requests: list = field(default_factory=list)
    last_request: float = 0


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter.

        Args:
            config: Rate limit configuration.
        """
        self.config = config or RateLimitConfig()
        self.clients: Dict[str, ClientRateInfo] = defaultdict(ClientRateInfo)

    def _get_client_key(self, request: Request) -> str:
        """Get client identifier from request.

        Args:
            request: FastAPI request object.

        Returns:
            Client identifier string.
        """
        # Try to get real IP from forwarded headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        return "unknown"

    def _cleanup_old_requests(self, client_info: ClientRateInfo, now: float) -> None:
        """Remove expired request timestamps.

        Args:
            client_info: Client rate information.
            now: Current timestamp.
        """
        minute_ago = now - 60
        hour_ago = now - 3600

        client_info.minute_requests = [
            t for t in client_info.minute_requests if t > minute_ago
        ]
        client_info.hour_requests = [
            t for t in client_info.hour_requests if t > hour_ago
        ]

    def is_allowed(self, request: Request) -> tuple[bool, Optional[dict]]:
        """Check if request is allowed under rate limits.

        Args:
            request: FastAPI request object.

        Returns:
            Tuple of (is_allowed, rate_info).
        """
        client_key = self._get_client_key(request)
        client_info = self.clients[client_key]
        now = time.time()

        self._cleanup_old_requests(client_info, now)

        # Check limits
        minute_count = len(client_info.minute_requests)
        hour_count = len(client_info.hour_requests)

        rate_info = {
            "X-RateLimit-Limit": str(self.config.requests_per_minute),
            "X-RateLimit-Remaining": str(
                max(0, self.config.requests_per_minute - minute_count)
            ),
            "X-RateLimit-Reset": str(int(now + 60)),
        }

        if minute_count >= self.config.requests_per_minute:
            rate_info["Retry-After"] = "60"
            return False, rate_info

        if hour_count >= self.config.requests_per_hour:
            rate_info["Retry-After"] = "3600"
            return False, rate_info

        # Record request
        client_info.minute_requests.append(now)
        client_info.hour_requests.append(now)
        client_info.last_request = now

        return True, rate_info

    def reset_client(self, client_key: str) -> None:
        """Reset rate limit for a client.

        Args:
            client_key: Client identifier.
        """
        if client_key in self.clients:
            del self.clients[client_key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    def __init__(
        self,
        app,
        config: Optional[RateLimitConfig] = None,
        exclude_paths: Optional[list[str]] = None,
    ):
        """Initialize middleware.

        Args:
            app: FastAPI application.
            config: Rate limit configuration.
            exclude_paths: Paths to exclude from rate limiting.
        """
        super().__init__(app)
        self.limiter = RateLimiter(config)
        self.exclude_paths = exclude_paths or ["/api/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting.

        Args:
            request: FastAPI request object.
            call_next: Next middleware/handler.

        Returns:
            Response object.
        """
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        is_allowed, rate_info = self.limiter.is_allowed(request)

        if not is_allowed:
            response = Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )
            # Add rate limit headers
            for key, value in (rate_info or {}).items():
                response.headers[key] = value
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        if rate_info:
            for key, value in rate_info.items():
                if not key.startswith("Retry"):
                    response.headers[key] = value

        return response


# Singleton rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """Get or create rate limiter singleton.

    Args:
        config: Optional configuration.

    Returns:
        RateLimiter instance.
    """
    global _rate_limiter

    if _rate_limiter is None:
        _rate_limiter = RateLimiter(config)

    return _rate_limiter

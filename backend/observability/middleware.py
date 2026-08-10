"""
PrMO - Observability Middleware
Request/response logging and metrics middleware.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from observability.logging import request_logger, get_logger

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app: ASGIApp, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Start timing
        start_time = time.perf_counter()

        # Extract client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Extract user info if available
        user_id = None
        user_email = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id
            user_email = request.state.user.email

        # Log request start
        logger.debug(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=client_ip,
            user_id=user_id,
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log request completion
            request_logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=user_id,
                user_email=user_email,
                ip_address=client_ip,
                user_agent=user_agent,
                request_id=request_id,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            request_logger.log_error(
                method=request.method,
                path=request.url.path,
                error=e,
                user_id=user_id,
                user_email=user_email,
                ip_address=client_ip,
                request_id=request_id,
            )

            # Re-raise
            raise


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic audit logging of sensitive operations."""

    # Actions that should be audited
    AUDIT_ACTIONS = {
        "POST": "CREATE",
        "PUT": "UPDATE",
        "PATCH": "UPDATE",
        "DELETE": "DELETE",
    }

    # Resource types by path prefix
    RESOURCE_MAP = {
        "/users": "user",
        "/tools": "tool",
        "/skills": "skill",
        "/prompts": "prompt",
        "/integrations": "integration",
        "/admin": "admin",
    }

    def __init__(self, app: ASGIApp, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json", "/auth"]

    def _get_resource_type(self, path: str) -> str:
        """Determine resource type from path."""
        for prefix, resource in self.RESOURCE_MAP.items():
            if path.startswith(prefix):
                return resource
        return "unknown"

    def _get_resource_id(self, path: str) -> int | None:
        """Extract resource ID from path if present."""
        parts = path.strip("/").split("/")
        if len(parts) >= 2 and parts[-1].isdigit():
            return int(parts[-1])
        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths and safe methods
        if request.url.path in self.excluded_paths or request.method not in self.AUDIT_ACTIONS:
            return await call_next(request)

        # Extract info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        user_id = None
        user_email = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id
            user_email = request.state.user.email

        resource_type = self._get_resource_type(request.url.path)
        resource_id = self._get_resource_id(request.url.path)
        action = self.AUDIT_ACTIONS.get(request.method, "UNKNOWN")

        # Process request
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log audit event for successful operations
            if response.status_code < 400:
                from observability.logging import audit_logger
                audit_logger.log_action(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    user_email=user_email,
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                    },
                    success=True,
                    ip_address=client_ip,
                    user_agent=user_agent,
                )

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log audit event for errors
            from observability.logging import audit_logger
            audit_logger.log_action(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id,
                user_email=user_email,
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 2),
                },
                success=False,
                error_message=str(e),
                ip_address=client_ip,
                user_agent=user_agent,
            )

            raise

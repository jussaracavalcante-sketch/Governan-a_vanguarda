"""
VANGUARDIAN - Observability Logging
Structured logging configuration using structlog.
"""
import sys
import logging
import structlog
from typing import Any, Dict
from config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RequestLogger:
    """Logger for HTTP requests with context."""

    def __init__(self):
        self.logger = get_logger("request")

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: int = None,
        user_email: str = None,
        ip_address: str = None,
        user_agent: str = None,
        **extra: Any,
    ) -> None:
        """Log an HTTP request with structured context."""
        self.logger.info(
            "http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            **extra,
        )

    def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        user_id: int = None,
        user_email: str = None,
        ip_address: str = None,
        **extra: Any,
    ) -> None:
        """Log an HTTP error with structured context."""
        self.logger.error(
            "http_error",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            **extra,
        )


class AuditLogger:
    """Logger for audit events."""

    def __init__(self):
        self.logger = get_logger("audit")

    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: int = None,
        user_id: int = None,
        user_email: str = None,
        details: Dict = None,
        success: bool = True,
        error_message: str = None,
        ip_address: str = None,
        user_agent: str = None,
    ) -> None:
        """Log an audit event."""
        self.logger.info(
            "audit_event",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            details=details,
            success=success,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
        )


class IntegrationLogger:
    """Logger for integration events."""

    def __init__(self):
        self.logger = get_logger("integration")

    def log_sync_start(
        self,
        integration_name: str,
        sync_type: str,
        integration_id: int,
    ) -> None:
        """Log integration sync start."""
        self.logger.info(
            "integration_sync_start",
            integration_name=integration_name,
            sync_type=sync_type,
            integration_id=integration_id,
        )

    def log_sync_complete(
        self,
        integration_name: str,
        sync_type: str,
        integration_id: int,
        records_processed: int,
        records_created: int,
        records_updated: int,
        records_failed: int,
        duration_seconds: int,
        status: str,
    ) -> None:
        """Log integration sync completion."""
        self.logger.info(
            "integration_sync_complete",
            integration_name=integration_name,
            sync_type=sync_type,
            integration_id=integration_id,
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            records_failed=records_failed,
            duration_seconds=duration_seconds,
            status=status,
        )

    def log_sync_error(
        self,
        integration_name: str,
        sync_type: str,
        integration_id: int,
        error: Exception,
    ) -> None:
        """Log integration sync error."""
        self.logger.error(
            "integration_sync_error",
            integration_name=integration_name,
            sync_type=sync_type,
            integration_id=integration_id,
            error_type=type(error).__name__,
            error_message=str(error),
        )


# Global logger instances
request_logger = RequestLogger()
audit_logger = AuditLogger()
integration_logger = IntegrationLogger()

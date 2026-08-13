"""
Gestão HEAD de IA - Observability Metrics
Prometheus metrics collection and exposition.
"""
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from config import get_settings

settings = get_settings()

# Application info
app_info = Info("head_ia_app", "Gestão HEAD de IA Application Information")
app_info.info({"version": "1.0.0", "name": "Gestão HEAD de IA API"})

# HTTP Metrics
http_requests_total = Counter(
    "head_ia_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "head_ia_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

http_requests_in_progress = Gauge(
    "head_ia_http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method", "endpoint"],
)

# Authentication Metrics
auth_login_total = Counter(
    "head_ia_auth_login_total",
    "Total login attempts",
    ["status"],  # success, failure
)

auth_token_refresh_total = Counter(
    "head_ia_auth_token_refresh_total",
    "Total token refresh attempts",
    ["status"],  # success, failure
)

auth_active_users = Gauge(
    "head_ia_auth_active_users",
    "Currently active users (with valid tokens)",
)

# Database Metrics
db_queries_total = Counter(
    "head_ia_db_queries_total",
    "Total database queries",
    ["operation", "table", "status"],  # status: success, error
)

db_query_duration_seconds = Histogram(
    "head_ia_db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

db_connections_active = Gauge(
    "head_ia_db_connections_active",
    "Active database connections",
)

# Business Metrics
business_users_total = Gauge(
    "head_ia_business_users_total",
    "Total users by role",
    ["role", "status"],
)

business_tools_total = Gauge(
    "head_ia_business_tools_total",
    "Total tools by status",
    ["status"],
)

business_skills_total = Gauge(
    "head_ia_business_skills_total",
    "Total skills by level",
    ["level"],
)

business_prompts_total = Gauge(
    "head_ia_business_prompts_total",
    "Total prompts",
)

# Integration Metrics
integration_sync_total = Counter(
    "head_ia_integration_sync_total",
    "Total integration sync operations",
    ["integration", "sync_type", "status"],
)

integration_sync_duration_seconds = Histogram(
    "head_ia_integration_sync_duration_seconds",
    "Integration sync duration in seconds",
    ["integration", "sync_type"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

integration_records_processed = Counter(
    "head_ia_integration_records_processed_total",
    "Total records processed by integrations",
    ["integration", "type"],  # type: created, updated, failed
)

integration_last_sync_timestamp = Gauge(
    "head_ia_integration_last_sync_timestamp",
    "Timestamp of last successful sync",
    ["integration"],
)

integration_enabled = Gauge(
    "head_ia_integration_enabled",
    "Integration enabled status (1=enabled, 0=disabled)",
    ["integration"],
)

# Audit Metrics
audit_events_total = Counter(
    "head_ia_audit_events_total",
    "Total audit events",
    ["action", "resource_type", "success"],
)

# System Metrics
system_uptime_seconds = Gauge(
    "head_ia_system_uptime_seconds",
    "Application uptime in seconds",
)

system_memory_usage_bytes = Gauge(
    "head_ia_system_memory_usage_bytes",
    "Memory usage in bytes",
    ["type"],  # rss, vms
)

system_cpu_usage_percent = Gauge(
    "head_ia_system_cpu_usage_percent",
    "CPU usage percentage",
)


def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def record_http_request_start(method: str, endpoint: str):
    """Record HTTP request start."""
    http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()


def record_http_request_end(method: str, endpoint: str):
    """Record HTTP request end."""
    http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


def record_login(success: bool):
    """Record login attempt."""
    auth_login_total.labels(status="success" if success else "failure").inc()


def record_token_refresh(success: bool):
    """Record token refresh attempt."""
    auth_token_refresh_total.labels(status="success" if success else "failure").inc()


def set_active_users(count: int):
    """Set active users gauge."""
    auth_active_users.set(count)


def record_db_query(operation: str, table: str, success: bool, duration: float):
    """Record database query metrics."""
    db_queries_total.labels(operation=operation, table=table, status="success" if success else "error").inc()
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)


def set_db_connections(count: int):
    """Set active database connections."""
    db_connections_active.set(count)


def update_business_metrics(
    users_by_role: dict = None,
    tools_by_status: dict = None,
    skills_by_level: dict = None,
    prompts_total: int = None,
):
    """Update business metrics."""
    if users_by_role:
        for (role, status), count in users_by_role.items():
            business_users_total.labels(role=role, status=status).set(count)

    if tools_by_status:
        for status, count in tools_by_status.items():
            business_tools_total.labels(status=status).set(count)

    if skills_by_level:
        for level, count in skills_by_level.items():
            business_skills_total.labels(level=level).set(count)

    if prompts_total is not None:
        business_prompts_total.set(prompts_total)


def record_integration_sync(
    integration: str,
    sync_type: str,
    status: str,
    duration: float,
    records_processed: int = 0,
    records_created: int = 0,
    records_updated: int = 0,
    records_failed: int = 0,
):
    """Record integration sync metrics."""
    integration_sync_total.labels(integration=integration, sync_type=sync_type, status=status).inc()
    integration_sync_duration_seconds.labels(integration=integration, sync_type=sync_type).observe(duration)

    if records_processed:
        integration_records_processed.labels(integration=integration, type="processed").inc(records_processed)
    if records_created:
        integration_records_processed.labels(integration=integration, type="created").inc(records_created)
    if records_updated:
        integration_records_processed.labels(integration=integration, type="updated").inc(records_updated)
    if records_failed:
        integration_records_processed.labels(integration=integration, type="failed").inc(records_failed)

    if status == "success":
        import time
        integration_last_sync_timestamp.labels(integration=integration).set(time.time())


def set_integration_enabled(integration: str, enabled: bool):
    """Set integration enabled status."""
    integration_enabled.labels(integration=integration).set(1 if enabled else 0)


def record_audit_event(action: str, resource_type: str, success: bool):
    """Record audit event."""
    audit_events_total.labels(action=action, resource_type=resource_type, success="true" if success else "false").inc()


def set_uptime(seconds: float):
    """Set system uptime."""
    system_uptime_seconds.set(seconds)


def set_memory_usage(rss: int, vms: int):
    """Set memory usage."""
    system_memory_usage_bytes.labels(type="rss").set(rss)
    system_memory_usage_bytes.labels(type="vms").set(vms)


def set_cpu_usage(percent: float):
    """Set CPU usage."""
    system_cpu_usage_percent.set(percent)


async def metrics_endpoint() -> Response:
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

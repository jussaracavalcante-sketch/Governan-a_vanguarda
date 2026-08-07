"""
VANGUARDIAN - Observability Health Checks
Liveness and readiness probes for Kubernetes/container orchestration.
"""
import time
import psutil
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, engine
from config import get_settings
from observability.metrics import set_uptime, set_memory_usage, set_cpu_usage

settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health"])

# Track application start time
_start_time = time.time()


@router.get("/live", summary="Liveness probe")
async def liveness() -> Dict[str, Any]:
    """
    Liveness probe - indicates if the application is running.
    Used by Kubernetes to determine if container should be restarted.
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - _start_time,
    }


@router.get("/ready", summary="Readiness probe")
async def readiness(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness probe - indicates if the application can serve requests.
    Checks database connectivity and critical dependencies.
    """
    checks = {}
    overall_ready = True

    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_ready = False

    # Check disk space
    try:
        disk = psutil.disk_usage("/")
        disk_free_percent = (disk.free / disk.total) * 100
        checks["disk"] = {
            "status": "healthy" if disk_free_percent > 10 else "warning",
            "free_percent": round(disk_free_percent, 1),
            "free_gb": round(disk.free / (1024**3), 2),
        }
        if disk_free_percent <= 10:
            overall_ready = False
    except Exception as e:
        checks["disk"] = {"status": "unknown", "error": str(e)}

    # Check memory
    try:
        memory = psutil.virtual_memory()
        checks["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "used_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
        }
        if memory.percent >= 90:
            overall_ready = False
    except Exception as e:
        checks["memory"] = {"status": "unknown", "error": str(e)}

    # Update metrics
    set_uptime(time.time() - _start_time)
    try:
        process = psutil.Process()
        mem_info = process.memory_info()
        set_memory_usage(mem_info.rss, mem_info.vms)
        set_cpu_usage(process.cpu_percent())
    except Exception:
        pass

    response = {
        "status": "ready" if overall_ready else "not_ready",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - _start_time,
        "checks": checks,
    }

    if not overall_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response,
        )

    return response


@router.get("/startup", summary="Startup probe")
async def startup() -> Dict[str, Any]:
    """
    Startup probe - indicates if the application has finished initialization.
    Used by Kubernetes to determine when to start sending traffic.
    """
    # Check if database tables exist
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]

        required_tables = ["users", "tools", "skills", "prompts", "activities", "audit_logs", "integration_configs"]
        missing_tables = [t for t in required_tables if t not in tables]

        if missing_tables:
            return {
                "status": "initializing",
                "message": f"Missing tables: {', '.join(missing_tables)}",
                "timestamp": time.time(),
            }
    except Exception as e:
        return {
            "status": "initializing",
            "message": f"Database check failed: {str(e)}",
            "timestamp": time.time(),
        }

    return {
        "status": "started",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - _start_time,
    }


@router.get("/metrics", summary="Prometheus metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from observability.metrics import metrics_endpoint
    return await metrics_endpoint()

"""
VANGUARDIAN - Main Application
FastAPI entrypoint with auth, admin, observability and core routers.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from config import get_settings
import routes_users, routes_tools, routes_skills, routes_prompts, routes_dashboard
from auth.router import router as auth_router
from admin.router import router as admin_router
from observability.health import router as health_router
from observability.logging import configure_logging, get_logger
from observability.middleware import RequestLoggingMiddleware, AuditMiddleware
from integrations.router import router as integrations_router
from crud import seed_initial_data

settings = get_settings()
configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", app=settings.app_name, version=settings.version)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    except Exception as exc:
        logger.error("seed_failed", error=str(exc))
    finally:
        db.close()
    yield
    logger.info("shutdown", app=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description=(
        "API de governança digital VANGUARDIAN: controle de acessos, "
        "ferramentas, skills, prompts, autenticação, admin, observabilidade "
        "e integrações (RD Station, ICLIPS, VJOB)."
    ),
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(health_router)
app.include_router(integrations_router)
app.include_router(routes_users.router)
app.include_router(routes_tools.router)
app.include_router(routes_skills.router)
app.include_router(routes_prompts.router)
app.include_router(routes_dashboard.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/health/live",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)

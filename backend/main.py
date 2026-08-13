"""
Gestão HEAD de IA - Main Application
FastAPI entrypoint: autenticação, observabilidade e o app do HEAD de IA
(ativos, tarefas, licenças, indicadores/KPIs, relatórios, processos,
base de conhecimento) + Visão do PrMO (somente consulta).
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from config import get_settings
from crud import seed_admin
from auth.router import router as auth_router
from observability.health import router as health_router
from observability.logging import configure_logging, get_logger
from observability.middleware import RequestLoggingMiddleware
import head.models  # noqa: F401  (registra as tabelas do módulo HEAD de IA no metadata)
from head.router import router as head_router
from head.seed import seed_head_data

settings = get_settings()
configure_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", app=settings.app_name, version=settings.version)
    # Init de banco resiliente: uma falha de conexão não derruba o app —
    # fica logada e o estado real aparece em /health/ready.
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_admin(db)
            seed_head_data(db)
        finally:
            db.close()
        logger.info("db_ready")
    except Exception as exc:
        logger.error("db_init_failed", error=str(exc))
    yield
    logger.info("shutdown", app=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description=(
        "API do app Gestão HEAD de IA: controle de ativos, tarefas do dia a dia, "
        "indicadores/KPIs, relatórios mensais, controle de licenças, otimização de "
        "processos e base de conhecimento. Inclui a Visão do PrMO (somente consulta)."
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
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(head_router)


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

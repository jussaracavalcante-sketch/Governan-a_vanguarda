from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

_is_sqlite = "sqlite" in settings.database_url

# Para bancos hospedados (Supabase/PostgreSQL atrás de pooler) usamos
# pool_pre_ping + pool_recycle para descartar conexões ociosas/derrubadas
# pelo pooler antes de reutilizá-las. Para SQLite mantemos o comportamento padrão.
_engine_kwargs = dict(echo=settings.debug)
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_pre_ping"] = True
    _engine_kwargs["pool_recycle"] = 1800

engine = create_engine(settings.database_url, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if "sqlite" in settings.database_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

# Monta a URL do banco. Se DB_PASSWORD estiver definido, injeta a senha com
# segurança (sem exigir URL-encoding de caracteres especiais na DATABASE_URL).
_url = make_url(settings.database_url)
if settings.db_password:
    _url = _url.set(password=settings.db_password)
_is_sqlite = _url.get_backend_name() == "sqlite"

engine = create_engine(
    _url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    echo=settings.debug,
)

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
    if _is_sqlite:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

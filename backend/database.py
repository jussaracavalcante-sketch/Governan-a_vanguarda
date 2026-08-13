from sqlalchemy import create_engine, event, text
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

_SQLITE_FALLBACK = "sqlite:///./head_ia.db"


def _build_engine(url, is_sqlite):
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if is_sqlite else {},
        pool_pre_ping=not is_sqlite,
        echo=settings.debug,
    )


engine = _build_engine(_url, _is_sqlite)

# Resiliência: se o banco configurado (ex.: Postgres/Supabase) não conectar,
# cai para SQLite local para o app continuar no ar. Se as credenciais estiverem
# corretas, usa o banco configurado normalmente (com persistência).
if not _is_sqlite:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        print(
            f"[database] Falha ao conectar em '{_url.render_as_string(hide_password=True)}': "
            f"{exc}. Usando SQLite local (dados NÃO persistem entre deploys). "
            f"Corrija DATABASE_URL/DB_PASSWORD para persistir no Postgres."
        )
        try:
            engine.dispose()
        except Exception:  # noqa: BLE001
            pass
        _url = make_url(_SQLITE_FALLBACK)
        _is_sqlite = True
        engine = _build_engine(_url, True)

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

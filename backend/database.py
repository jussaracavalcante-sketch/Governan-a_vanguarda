from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

# Monta a URL do banco. DB_PASSWORD só é aplicado quando a URL NÃO traz senha
# (não sobrescreve uma senha já embutida na DATABASE_URL).
_url = make_url(settings.database_url)
if settings.db_password and not _url.password:
    _url = _url.set(password=settings.db_password)
_is_sqlite = _url.get_backend_name() == "sqlite"

_SQLITE_FALLBACK = "sqlite:///./head_ia.db"


def _build_engine(url, is_sqlite):
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if is_sqlite else {"connect_timeout": 10},
        pool_pre_ping=not is_sqlite,
        echo=settings.debug,
    )


def _swap_pooler_host(url):
    """Alterna o nó do pooler Supabase (aws-0 <-> aws-1)."""
    host = url.host or ""
    if "aws-0-" in host:
        return url.set(host=host.replace("aws-0-", "aws-1-"))
    if "aws-1-" in host:
        return url.set(host=host.replace("aws-1-", "aws-0-"))
    return None


def _connect(url, is_sqlite):
    eng = _build_engine(url, is_sqlite)
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return eng


if _is_sqlite:
    engine = _build_engine(_url, True)
else:
    # Resiliência: tenta o host informado; se falhar, o nó alternativo do pooler;
    # se ainda assim falhar, cai para SQLite local (app continua no ar).
    engine = None
    try:
        engine = _connect(_url, False)
    except Exception as exc1:  # noqa: BLE001
        alt = _swap_pooler_host(_url)
        if alt is not None:
            try:
                engine = _connect(alt, False)
                _url = alt
            except Exception:  # noqa: BLE001
                engine = None
        if engine is None:
            print(
                f"[database] Postgres indisponível ({exc1}). Usando SQLite local "
                f"(dados NÃO persistem entre deploys). Verifique DATABASE_URL."
            )
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

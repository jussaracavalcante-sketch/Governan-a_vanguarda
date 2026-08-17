"""
Sincronização automática das atividades (Jira / Google Drive / Gmail).

Executado pelo Render Cron 3x/dia. Puxa as atividades das APIs de cada
ferramenta e faz upsert em `head_activities`, atualizando `head_sync_state`.

Uso local:  cd backend && python sync_activities.py
"""
import sys

from database import engine, Base, SessionLocal
import head.models  # noqa: F401  (registra as tabelas do módulo HEAD)
from head.connectors import sync_all


def main() -> int:
    # Garante que as tabelas existem antes de sincronizar.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = sync_all(db)
    finally:
        db.close()

    total = result.get("created", 0)
    print(f"[sync] concluído — {total} novas atividades")
    for src in result.get("sources", []):
        print(f"  - {src.get('source')}: ok={src.get('ok')} "
              f"criadas={src.get('created', 0)} total={src.get('total', '-')}"
              + (f" erro={src.get('error')}" if src.get("error") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

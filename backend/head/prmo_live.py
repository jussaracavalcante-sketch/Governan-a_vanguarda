"""
Visão do PrMO — consulta AO VIVO (somente leitura).

Quando PRMO_DATABASE_URL está definido, o HEAD lê o banco de governança do PrMO
em tempo real e monta o mesmo formato do snapshot. Somente SELECT — o HEAD nunca
grava no PrMO.
"""
from datetime import date
from functools import lru_cache

from sqlalchemy import create_engine, text

_REGISTRY_LABELS = {
    "asset": "Ativos de IA",
    "knowledge": "Base de conhecimento",
    "diagnostic": "Diagnósticos",
    "risk": "Riscos",
    "plan30": "Plano 30 dias",
    "opportunity": "Oportunidades",
}


@lru_cache(maxsize=2)
def _engine(url: str):
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=2,
        pool_recycle=1800,
        connect_args={"connect_timeout": 10},
    )


def get_prmo_live(url: str) -> dict:
    """Lê o PrMO ao vivo e retorna o retrato consultivo. Levanta em caso de falha."""
    eng = _engine(url)
    with eng.connect() as c:
        reg = c.execute(text("select registry, count(*) as n from gov_registry group by registry")).fetchall()
        total = c.execute(text("select count(*) from gov_registry")).scalar() or 0
        adoption = c.execute(text("select area, percent from gov_adoption order by percent desc")).fetchall()
        initiatives = c.execute(text("select name, area, status, hours_saved from gov_initiatives")).fetchall()
        incidents = c.execute(text("select title, area, criticality, status from gov_incidents")).fetchall()
        clients = c.execute(text("select name, segment, stage, ai_usage from gov_clients")).fetchall()
        hours = c.execute(text("select coalesce(sum(hours_saved),0) from gov_initiatives")).scalar() or 0

    by_type = [{"label": _REGISTRY_LABELS.get(r[0], str(r[0]).title()), "count": int(r[1])} for r in reg]
    by_type.sort(key=lambda x: x["count"], reverse=True)

    return {
        "as_of": date.today().isoformat(),
        "source": "PrMO · Governança de IA (consulta ao vivo)",
        "live": True,
        "registry": {"total": int(total), "by_type": by_type},
        "adoption": [{"area": a[0], "percent": a[1]} for a in adoption],
        "initiatives": [
            {"name": i[0], "area": i[1], "status": i[2], "hours_saved": i[3]} for i in initiatives
        ],
        "incidents": [
            {"title": x[0], "area": x[1], "criticality": x[2], "status": x[3]} for x in incidents
        ],
        "clients": [
            {"name": c2[0], "segment": c2[1], "stage": c2[2], "ai_usage": c2[3]} for c2 in clients
        ],
        "hours_saved_total": float(hours),
    }

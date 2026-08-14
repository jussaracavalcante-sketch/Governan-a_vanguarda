"""
PRMO · Gestão HEAD de IA - Router
Endpoints REST para ativos, tarefas, licenças, indicadores/KPIs,
base de conhecimento, dashboard e relatório mensal.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user, get_current_manager_user
from models import User
from head import crud, schemas
from head.prmo_snapshot import PRMO_SNAPSHOT

router = APIRouter(prefix="/head", tags=["Gestão HEAD de IA"])


# ─────────────────────────── Dashboard & Relatório ───────────────────────────
@router.get("/dashboard", response_model=schemas.HeadDashboard)
def head_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.get_dashboard(db)


@router.get("/prmo", summary="Visão do PrMO (consultivo, somente leitura)")
def prmo_view(user: User = Depends(get_current_user)):
    """Retrato de governança do PrMO. Ao vivo se PRMO_DATABASE_URL estiver
    configurado; caso contrário, usa o snapshot fixo. Somente leitura."""
    from config import get_settings

    settings = get_settings()
    if settings.prmo_database_url:
        try:
            from head.prmo_live import get_prmo_live
            return get_prmo_live(settings.prmo_database_url)
        except Exception as exc:
            # Falha na leitura ao vivo → cai para o snapshot (não quebra a tela).
            data = dict(PRMO_SNAPSHOT)
            data["live"] = False
            data["_diag"] = f"configured=1 err={type(exc).__name__}: {str(exc)[:180]}"
            return data
    data = dict(PRMO_SNAPSHOT)
    data["live"] = False
    data["_diag"] = "configured=0 (PRMO_DATABASE_URL vazio no ambiente)"
    return data


@router.get("/report/{period}", response_model=schemas.MonthlyReport)
def monthly_report(period: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if len(period) != 7 or period[4] != "-":
        raise HTTPException(status_code=422, detail="Período inválido. Use o formato YYYY-MM.")
    return crud.get_monthly_report(db, period)


# ─────────────────────────── Ativos ───────────────────────────
@router.get("/assets", response_model=List[schemas.AssetResponse])
def list_assets(
    search: str = Query(""), status: str = Query(""), asset_type: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return crud.get_assets(db, search=search, status=status, asset_type=asset_type)


@router.post("/assets", response_model=schemas.AssetResponse, status_code=201)
def create_asset(item: schemas.AssetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    return crud.create_asset(db, item)


@router.put("/assets/{item_id}", response_model=schemas.AssetResponse)
def update_asset(item_id: int, item: schemas.AssetUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    obj = crud.update_asset(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return obj


@router.delete("/assets/{item_id}", status_code=204)
def delete_asset(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    if not crud.delete_asset(db, item_id):
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return None


# ─────────────────────────── Tarefas ───────────────────────────
@router.get("/tasks", response_model=List[schemas.TaskResponse])
def list_tasks(
    search: str = Query(""), status: str = Query(""), task_date: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return crud.get_tasks(db, search=search, status=status, task_date=task_date)


@router.post("/tasks", response_model=schemas.TaskResponse, status_code=201)
def create_task(item: schemas.TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.create_task(db, item)


@router.put("/tasks/{item_id}", response_model=schemas.TaskResponse)
def update_task(item_id: int, item: schemas.TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    obj = crud.update_task(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return obj


@router.delete("/tasks/{item_id}", status_code=204)
def delete_task(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not crud.delete_task(db, item_id):
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return None


# ─────────────────────────── Licenças ───────────────────────────
@router.get("/licenses", response_model=List[schemas.LicenseResponse])
def list_licenses(
    search: str = Query(""), status: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return crud.get_licenses(db, search=search, status=status)


@router.post("/licenses", response_model=schemas.LicenseResponse, status_code=201)
def create_license(item: schemas.LicenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    return crud.create_license(db, item)


@router.put("/licenses/{item_id}", response_model=schemas.LicenseResponse)
def update_license(item_id: int, item: schemas.LicenseUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    obj = crud.update_license(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Licença não encontrada")
    return obj


@router.delete("/licenses/{item_id}", status_code=204)
def delete_license(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    if not crud.delete_license(db, item_id):
        raise HTTPException(status_code=404, detail="Licença não encontrada")
    return None


# ─────────────────────────── Indicadores / KPIs ───────────────────────────
@router.get("/indicators", response_model=List[schemas.IndicatorResponse])
def list_indicators(
    search: str = Query(""), period: str = Query(""), category: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return crud.get_indicators(db, search=search, period=period, category=category)


@router.post("/indicators", response_model=schemas.IndicatorResponse, status_code=201)
def create_indicator(item: schemas.IndicatorCreate, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    return crud.create_indicator(db, item)


@router.put("/indicators/{item_id}", response_model=schemas.IndicatorResponse)
def update_indicator(item_id: int, item: schemas.IndicatorUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    obj = crud.update_indicator(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")
    return obj


@router.delete("/indicators/{item_id}", status_code=204)
def delete_indicator(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    if not crud.delete_indicator(db, item_id):
        raise HTTPException(status_code=404, detail="Indicador não encontrado")
    return None


# ─────────────────────────── Otimização de Processos ───────────────────────────
@router.get("/processes", response_model=List[schemas.ProcessResponse])
def list_processes(
    search: str = Query(""), stage: str = Query(""), status: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return crud.get_processes(db, search=search, stage=stage, status=status)


@router.post("/processes", response_model=schemas.ProcessResponse, status_code=201)
def create_process(item: schemas.ProcessCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.create_process(db, item)


@router.put("/processes/{item_id}", response_model=schemas.ProcessResponse)
def update_process(item_id: int, item: schemas.ProcessUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    obj = crud.update_process(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return obj


@router.delete("/processes/{item_id}", status_code=204)
def delete_process(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    if not crud.delete_process(db, item_id):
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return None


# ─────────────────────────── Base de conhecimento ───────────────────────────
@router.get("/knowledge", response_model=List[schemas.KnowledgeResponse])
def list_articles(
    search: str = Query(""), category: str = Query(""), status: str = Query(""),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    return crud.get_articles(db, search=search, category=category, status=status)


@router.post("/knowledge", response_model=schemas.KnowledgeResponse, status_code=201)
def create_article(item: schemas.KnowledgeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.create_article(db, item)


@router.put("/knowledge/{item_id}", response_model=schemas.KnowledgeResponse)
def update_article(item_id: int, item: schemas.KnowledgeUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    obj = crud.update_article(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return obj


@router.delete("/knowledge/{item_id}", status_code=204)
def delete_article(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_manager_user)):
    if not crud.delete_article(db, item_id):
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return None

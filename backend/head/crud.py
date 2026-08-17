"""
PRMO · Gestão HEAD de IA - CRUD
Operações de banco para ativos, tarefas, licenças, indicadores e conhecimento,
além das agregações de dashboard e relatório mensal.
"""
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from head.models import Asset, DailyTask, License, Indicator, KnowledgeArticle, ProcessImprovement, Activity, PurchaseRequest, SyncState
from head import schemas


# ─────────────────────────── Helpers genéricos ───────────────────────────
def _create(db: Session, model, data):
    obj = model(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _update(db: Session, obj, data):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def _delete(db: Session, obj):
    db.delete(obj)
    db.commit()
    return obj


# ─────────────────────────── Ativos ───────────────────────────
def create_asset(db: Session, data: schemas.AssetCreate) -> Asset:
    return _create(db, Asset, data)


def get_assets(db: Session, skip=0, limit=200, search="", status="", asset_type=""):
    q = db.query(Asset)
    if search:
        q = q.filter(or_(Asset.name.ilike(f"%{search}%"), Asset.vendor.ilike(f"%{search}%"), Asset.owner.ilike(f"%{search}%")))
    if status:
        q = q.filter(Asset.status == status)
    if asset_type:
        q = q.filter(Asset.asset_type == asset_type)
    return q.order_by(Asset.name).offset(skip).limit(limit).all()


def get_asset(db: Session, asset_id: int):
    return db.query(Asset).filter(Asset.id == asset_id).first()


def update_asset(db: Session, asset_id: int, data: schemas.AssetUpdate):
    obj = get_asset(db, asset_id)
    return _update(db, obj, data) if obj else None


def delete_asset(db: Session, asset_id: int):
    obj = get_asset(db, asset_id)
    return _delete(db, obj) if obj else None


# ─────────────────────────── Tarefas ───────────────────────────
def create_task(db: Session, data: schemas.TaskCreate) -> DailyTask:
    return _create(db, DailyTask, data)


def get_tasks(db: Session, skip=0, limit=200, search="", status="", task_date=""):
    q = db.query(DailyTask)
    if search:
        q = q.filter(or_(DailyTask.title.ilike(f"%{search}%"), DailyTask.responsible.ilike(f"%{search}%")))
    if status:
        q = q.filter(DailyTask.status == status)
    if task_date:
        q = q.filter(DailyTask.task_date == task_date)
    return q.order_by(DailyTask.task_date.desc(), DailyTask.id.desc()).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int):
    return db.query(DailyTask).filter(DailyTask.id == task_id).first()


def update_task(db: Session, task_id: int, data: schemas.TaskUpdate):
    obj = get_task(db, task_id)
    return _update(db, obj, data) if obj else None


def delete_task(db: Session, task_id: int):
    obj = get_task(db, task_id)
    return _delete(db, obj) if obj else None


# ─────────────────────────── Licenças ───────────────────────────
def create_license(db: Session, data: schemas.LicenseCreate) -> License:
    return _create(db, License, data)


def get_licenses(db: Session, skip=0, limit=200, search="", status=""):
    q = db.query(License)
    if search:
        q = q.filter(or_(License.software.ilike(f"%{search}%"), License.vendor.ilike(f"%{search}%")))
    if status:
        q = q.filter(License.status == status)
    return q.order_by(License.software).offset(skip).limit(limit).all()


def get_license(db: Session, license_id: int):
    return db.query(License).filter(License.id == license_id).first()


def update_license(db: Session, license_id: int, data: schemas.LicenseUpdate):
    obj = get_license(db, license_id)
    return _update(db, obj, data) if obj else None


def delete_license(db: Session, license_id: int):
    obj = get_license(db, license_id)
    return _delete(db, obj) if obj else None


# ─────────────────────────── Indicadores / KPIs ───────────────────────────
def create_indicator(db: Session, data: schemas.IndicatorCreate) -> Indicator:
    return _create(db, Indicator, data)


def get_indicators(db: Session, skip=0, limit=200, search="", period="", category=""):
    q = db.query(Indicator)
    if search:
        q = q.filter(Indicator.name.ilike(f"%{search}%"))
    if period:
        q = q.filter(Indicator.period == period)
    if category:
        q = q.filter(Indicator.category == category)
    return q.order_by(Indicator.period.desc(), Indicator.name).offset(skip).limit(limit).all()


def get_indicator(db: Session, indicator_id: int):
    return db.query(Indicator).filter(Indicator.id == indicator_id).first()


def update_indicator(db: Session, indicator_id: int, data: schemas.IndicatorUpdate):
    obj = get_indicator(db, indicator_id)
    return _update(db, obj, data) if obj else None


def delete_indicator(db: Session, indicator_id: int):
    obj = get_indicator(db, indicator_id)
    return _delete(db, obj) if obj else None


# ─────────────────────────── Base de conhecimento ───────────────────────────
def create_article(db: Session, data: schemas.KnowledgeCreate) -> KnowledgeArticle:
    return _create(db, KnowledgeArticle, data)


def get_articles(db: Session, skip=0, limit=200, search="", category="", status=""):
    q = db.query(KnowledgeArticle)
    if search:
        q = q.filter(or_(
            KnowledgeArticle.title.ilike(f"%{search}%"),
            KnowledgeArticle.summary.ilike(f"%{search}%"),
            KnowledgeArticle.tags.ilike(f"%{search}%"),
        ))
    if category:
        q = q.filter(KnowledgeArticle.category == category)
    if status:
        q = q.filter(KnowledgeArticle.status == status)
    return q.order_by(KnowledgeArticle.updated_date.desc(), KnowledgeArticle.id.desc()).offset(skip).limit(limit).all()


def get_article(db: Session, article_id: int):
    return db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()


def update_article(db: Session, article_id: int, data: schemas.KnowledgeUpdate):
    obj = get_article(db, article_id)
    return _update(db, obj, data) if obj else None


def delete_article(db: Session, article_id: int):
    obj = get_article(db, article_id)
    return _delete(db, obj) if obj else None


# ─────────────────────────── Otimização de Processos ───────────────────────────
def create_process(db: Session, data: schemas.ProcessCreate) -> ProcessImprovement:
    return _create(db, ProcessImprovement, data)


def get_processes(db: Session, skip=0, limit=200, search="", stage="", status=""):
    q = db.query(ProcessImprovement)
    if search:
        q = q.filter(or_(
            ProcessImprovement.name.ilike(f"%{search}%"),
            ProcessImprovement.area.ilike(f"%{search}%"),
            ProcessImprovement.owner.ilike(f"%{search}%"),
        ))
    if stage:
        q = q.filter(ProcessImprovement.stage == stage)
    if status:
        q = q.filter(ProcessImprovement.status == status)
    return q.order_by(ProcessImprovement.id.desc()).offset(skip).limit(limit).all()


def get_process(db: Session, process_id: int):
    return db.query(ProcessImprovement).filter(ProcessImprovement.id == process_id).first()


def update_process(db: Session, process_id: int, data: schemas.ProcessUpdate):
    obj = get_process(db, process_id)
    return _update(db, obj, data) if obj else None


def delete_process(db: Session, process_id: int):
    obj = get_process(db, process_id)
    return _delete(db, obj) if obj else None


# ─────────────────────────── Dashboard ───────────────────────────
def _kpi_on_target(ind: Indicator) -> bool:
    """KPI é considerado 'na meta' quando o realizado atinge/ultrapassa o alvo."""
    if ind.target is None or ind.target == 0:
        return ind.actual > 0
    return ind.actual >= ind.target


def get_dashboard(db: Session) -> schemas.HeadDashboard:
    period = date.today().strftime("%Y-%m")

    assets = db.query(Asset).all()
    total_assets = len(assets)
    active_assets = sum(1 for a in assets if a.status == "Ativo")
    assets_monthly_cost = sum(a.monthly_cost or 0 for a in assets)
    critical_assets = sum(1 for a in assets if a.criticality == "Crítica")

    tasks = db.query(DailyTask).all()
    total_tasks = len(tasks)
    tasks_done = sum(1 for t in tasks if t.status == "Concluída")
    tasks_pending = sum(1 for t in tasks if t.status == "Pendente")
    tasks_in_progress = sum(1 for t in tasks if t.status == "Em andamento")
    hours_this_month = sum(t.hours_spent or 0 for t in tasks if (t.task_date or "").startswith(period))

    licenses = db.query(License).all()
    total_licenses = len(licenses)
    licenses_monthly_cost = sum(l.monthly_cost or 0 for l in licenses)
    seats_total = sum(l.seats_total or 0 for l in licenses)
    seats_used = sum(l.seats_used or 0 for l in licenses)
    seats_utilization = round((seats_used / seats_total * 100), 1) if seats_total else 0.0
    licenses_renewing = sum(1 for l in licenses if l.status == "Em renovação")

    indicators = db.query(Indicator).all()
    total_indicators = len(indicators)
    kpis_on_target = sum(1 for i in indicators if _kpi_on_target(i))
    kpis_off_target = total_indicators - kpis_on_target

    articles = db.query(KnowledgeArticle).all()
    total_articles = len(articles)
    published_articles = sum(1 for a in articles if a.status == "Publicado")

    processes = db.query(ProcessImprovement).all()
    total_processes = len(processes)
    processes_done = sum(1 for p in processes if p.status == "Concluído")
    processes_in_progress = sum(1 for p in processes if p.status == "Em andamento")
    hours_saved = sum(max(0.0, (p.time_before or 0) - (p.time_after or 0)) for p in processes)
    cost_saved = sum(max(0.0, (p.cost_before or 0) - (p.cost_after or 0)) for p in processes)

    recent_tasks = get_tasks(db, limit=6)

    return schemas.HeadDashboard(
        total_assets=total_assets,
        active_assets=active_assets,
        assets_monthly_cost=round(assets_monthly_cost, 2),
        critical_assets=critical_assets,
        total_tasks=total_tasks,
        tasks_done=tasks_done,
        tasks_pending=tasks_pending,
        tasks_in_progress=tasks_in_progress,
        hours_this_month=round(hours_this_month, 1),
        total_licenses=total_licenses,
        licenses_monthly_cost=round(licenses_monthly_cost, 2),
        seats_total=seats_total,
        seats_used=seats_used,
        seats_utilization=seats_utilization,
        licenses_renewing=licenses_renewing,
        total_indicators=total_indicators,
        kpis_on_target=kpis_on_target,
        kpis_off_target=kpis_off_target,
        total_articles=total_articles,
        published_articles=published_articles,
        total_processes=total_processes,
        processes_done=processes_done,
        processes_in_progress=processes_in_progress,
        hours_saved=round(hours_saved, 1),
        cost_saved=round(cost_saved, 2),
        recent_tasks=recent_tasks,
    )


# ─────────────────────────── Relatório mensal ───────────────────────────
def get_monthly_report(db: Session, period: str) -> schemas.MonthlyReport:
    """Relatório consolidado do mês (period no formato YYYY-MM)."""
    month_tasks = db.query(DailyTask).filter(DailyTask.task_date.like(f"{period}%")).all()
    tasks_total = len(month_tasks)
    tasks_done = sum(1 for t in month_tasks if t.status == "Concluída")
    tasks_hours = round(sum(t.hours_spent or 0 for t in month_tasks), 1)

    by_status = {}
    for t in month_tasks:
        entry = by_status.setdefault(t.status, {"count": 0, "hours": 0.0})
        entry["count"] += 1
        entry["hours"] += t.hours_spent or 0
    tasks_by_status = [
        schemas.ReportTaskBreakdown(status=s, count=v["count"], hours=round(v["hours"], 1))
        for s, v in sorted(by_status.items())
    ]

    assets = db.query(Asset).all()
    assets_total = len(assets)
    assets_cost = round(sum(a.monthly_cost or 0 for a in assets), 2)

    licenses = db.query(License).all()
    licenses_total = len(licenses)
    licenses_cost = round(sum(l.monthly_cost or 0 for l in licenses), 2)

    indicators = db.query(Indicator).filter(Indicator.period == period).order_by(Indicator.category, Indicator.name).all()
    kpis_on = sum(1 for i in indicators if _kpi_on_target(i))
    kpis_off = len(indicators) - kpis_on

    return schemas.MonthlyReport(
        period=period,
        tasks_total=tasks_total,
        tasks_done=tasks_done,
        tasks_hours=tasks_hours,
        tasks_by_status=tasks_by_status,
        assets_total=assets_total,
        assets_monthly_cost=assets_cost,
        licenses_total=licenses_total,
        licenses_monthly_cost=licenses_cost,
        total_monthly_cost=round(assets_cost + licenses_cost, 2),
        indicators=indicators,
        kpis_on_target=kpis_on,
        kpis_off_target=kpis_off,
    )


# ─── Atividades ───
def get_activities(db: Session, source: str = "", limit: int = 200):
    q = db.query(Activity)
    if source:
        q = q.filter(Activity.source == source)
    return q.order_by(Activity.activity_date.desc(), Activity.id.desc()).limit(limit).all()


# ─── Sincronização automática ───
def get_sync_state(db: Session):
    return db.query(SyncState).order_by(SyncState.source.asc()).all()


# ─── Solicitações de Compra ───
def get_purchase_requests(db: Session, status: str = "", limit: int = 200):
    q = db.query(PurchaseRequest)
    if status:
        q = q.filter(PurchaseRequest.status == status)
    return q.order_by(PurchaseRequest.request_date.desc(), PurchaseRequest.id.desc()).limit(limit).all()

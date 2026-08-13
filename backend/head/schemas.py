"""
PRMO · Gestão HEAD de IA - Pydantic Schemas
Validação de request/response para ativos, tarefas, licenças, indicadores,
base de conhecimento, dashboard e relatório mensal.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


ASSET_TYPE = "^(Modelo LLM|Agente|Automação|Integração|Dataset|Infraestrutura|Plataforma)$"
ASSET_STATUS = "^(Ativo|Em avaliação|Descontinuado)$"
ENVIRONMENT = "^(Produção|Homologação|Desenvolvimento)$"
CRITICALITY = "^(Baixa|Média|Alta|Crítica)$"
TASK_STATUS = "^(Pendente|Em andamento|Concluída|Bloqueada)$"
PRIORITY = "^(Baixa|Média|Alta|Crítica)$"
LICENSE_STATUS = "^(Ativa|Em renovação|Expirada|Cancelada)$"
INDICATOR_CATEGORY = "^(Operacional|Financeiro|Adoção|Qualidade|Risco)$"
TREND = "^(Subindo|Estável|Caindo|Concluído|Planejado)$"
KNOWLEDGE_STATUS = "^(Rascunho|Publicado|Arquivado)$"
PROCESS_STAGE = "^(Mapeamento|Diagnóstico|Priorização|Redesenho|Implementação|Medição|Padronizado)$"
PROCESS_STATUS = "^(Pendente|Em andamento|Concluído|Pausado)$"
LEVEL3 = "^(Baixo|Médio|Alto)$"
AI_AUTOMATION = "^(Não|Parcial|Total)$"


# ─── Asset ───
class AssetBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=150)
    asset_type: str = Field(default="Modelo LLM", pattern=ASSET_TYPE)
    vendor: str = Field(default="", max_length=80)
    owner: str = Field(default="", max_length=120)
    status: str = Field(default="Ativo", pattern=ASSET_STATUS)
    environment: str = Field(default="Produção", pattern=ENVIRONMENT)
    criticality: str = Field(default="Média", pattern=CRITICALITY)
    monthly_cost: float = Field(default=0.0, ge=0)
    description: str = Field(default="")
    acquisition_date: str = Field(default="")


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    asset_type: Optional[str] = Field(None, pattern=ASSET_TYPE)
    vendor: Optional[str] = Field(None, max_length=80)
    owner: Optional[str] = Field(None, max_length=120)
    status: Optional[str] = Field(None, pattern=ASSET_STATUS)
    environment: Optional[str] = Field(None, pattern=ENVIRONMENT)
    criticality: Optional[str] = Field(None, pattern=CRITICALITY)
    monthly_cost: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    acquisition_date: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Daily Task ───
class TaskBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    responsible: str = Field(default="", max_length=120)
    category: str = Field(default="Operação", max_length=60)
    status: str = Field(default="Pendente", pattern=TASK_STATUS)
    priority: str = Field(default="Média", pattern=PRIORITY)
    task_date: str = Field(default="")
    hours_spent: float = Field(default=0.0, ge=0)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    responsible: Optional[str] = Field(None, max_length=120)
    category: Optional[str] = Field(None, max_length=60)
    status: Optional[str] = Field(None, pattern=TASK_STATUS)
    priority: Optional[str] = Field(None, pattern=PRIORITY)
    task_date: Optional[str] = None
    hours_spent: Optional[float] = Field(None, ge=0)


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── License ───
class LicenseBase(BaseSchema):
    software: str = Field(..., min_length=1, max_length=150)
    vendor: str = Field(default="", max_length=80)
    plan: str = Field(default="", max_length=80)
    seats_total: int = Field(default=0, ge=0)
    seats_used: int = Field(default=0, ge=0)
    monthly_cost: float = Field(default=0.0, ge=0)
    status: str = Field(default="Ativa", pattern=LICENSE_STATUS)
    renewal_date: str = Field(default="")
    owner: str = Field(default="", max_length=120)
    notes: str = Field(default="")


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BaseSchema):
    software: Optional[str] = Field(None, min_length=1, max_length=150)
    vendor: Optional[str] = Field(None, max_length=80)
    plan: Optional[str] = Field(None, max_length=80)
    seats_total: Optional[int] = Field(None, ge=0)
    seats_used: Optional[int] = Field(None, ge=0)
    monthly_cost: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern=LICENSE_STATUS)
    renewal_date: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=120)
    notes: Optional[str] = None


class LicenseResponse(LicenseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Indicator / KPI ───
class IndicatorBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=150)
    category: str = Field(default="Operacional", max_length=60)
    period: str = Field(default="", max_length=7)  # YYYY-MM
    unit: str = Field(default="", max_length=20)
    target: float = Field(default=0.0)
    actual: float = Field(default=0.0)
    trend: str = Field(default="Estável", pattern=TREND)
    notes: str = Field(default="")


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    category: Optional[str] = Field(None, max_length=60)
    period: Optional[str] = Field(None, max_length=7)
    unit: Optional[str] = Field(None, max_length=20)
    target: Optional[float] = None
    actual: Optional[float] = None
    trend: Optional[str] = Field(None, pattern=TREND)
    notes: Optional[str] = None


class IndicatorResponse(IndicatorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Knowledge Article ───
class KnowledgeBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="Geral", max_length=60)
    summary: str = Field(default="", max_length=300)
    content: str = Field(default="")
    tags: str = Field(default="", max_length=200)
    author: str = Field(default="", max_length=120)
    status: str = Field(default="Publicado", pattern=KNOWLEDGE_STATUS)
    updated_date: str = Field(default="")


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=60)
    summary: Optional[str] = Field(None, max_length=300)
    content: Optional[str] = None
    tags: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=120)
    status: Optional[str] = Field(None, pattern=KNOWLEDGE_STATUS)
    updated_date: Optional[str] = None


class KnowledgeResponse(KnowledgeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Otimização de Processos ───
class ProcessBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    area: str = Field(default="", max_length=80)
    owner: str = Field(default="", max_length=120)
    stage: str = Field(default="Mapeamento", pattern=PROCESS_STAGE)
    status: str = Field(default="Em andamento", pattern=PROCESS_STATUS)
    impact: str = Field(default="Médio", pattern=LEVEL3)
    effort: str = Field(default="Médio", pattern=LEVEL3)
    ai_automation: str = Field(default="Não", pattern=AI_AUTOMATION)
    problem: str = Field(default="")
    proposal: str = Field(default="")
    time_before: float = Field(default=0.0, ge=0)
    time_after: float = Field(default=0.0, ge=0)
    cost_before: float = Field(default=0.0, ge=0)
    cost_after: float = Field(default=0.0, ge=0)
    responsible: str = Field(default="", max_length=120)
    due_date: str = Field(default="")
    notes: str = Field(default="")


class ProcessCreate(ProcessBase):
    pass


class ProcessUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    area: Optional[str] = Field(None, max_length=80)
    owner: Optional[str] = Field(None, max_length=120)
    stage: Optional[str] = Field(None, pattern=PROCESS_STAGE)
    status: Optional[str] = Field(None, pattern=PROCESS_STATUS)
    impact: Optional[str] = Field(None, pattern=LEVEL3)
    effort: Optional[str] = Field(None, pattern=LEVEL3)
    ai_automation: Optional[str] = Field(None, pattern=AI_AUTOMATION)
    problem: Optional[str] = None
    proposal: Optional[str] = None
    time_before: Optional[float] = Field(None, ge=0)
    time_after: Optional[float] = Field(None, ge=0)
    cost_before: Optional[float] = Field(None, ge=0)
    cost_after: Optional[float] = Field(None, ge=0)
    responsible: Optional[str] = Field(None, max_length=120)
    due_date: Optional[str] = None
    notes: Optional[str] = None


class ProcessResponse(ProcessBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Dashboard / Relatório ───
class HeadDashboard(BaseSchema):
    total_assets: int
    active_assets: int
    assets_monthly_cost: float
    critical_assets: int
    total_tasks: int
    tasks_done: int
    tasks_pending: int
    tasks_in_progress: int
    hours_this_month: float
    total_licenses: int
    licenses_monthly_cost: float
    seats_total: int
    seats_used: int
    seats_utilization: float
    licenses_renewing: int
    total_indicators: int
    kpis_on_target: int
    kpis_off_target: int
    total_articles: int
    published_articles: int
    total_processes: int
    processes_done: int
    processes_in_progress: int
    hours_saved: float
    cost_saved: float
    recent_tasks: List[TaskResponse]


class ReportTaskBreakdown(BaseSchema):
    status: str
    count: int
    hours: float


class MonthlyReport(BaseSchema):
    period: str
    tasks_total: int
    tasks_done: int
    tasks_hours: float
    tasks_by_status: List[ReportTaskBreakdown]
    assets_total: int
    assets_monthly_cost: float
    licenses_total: int
    licenses_monthly_cost: float
    total_monthly_cost: float
    indicators: List[IndicatorResponse]
    kpis_on_target: int
    kpis_off_target: int

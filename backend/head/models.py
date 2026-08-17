"""
PRMO · Gestão HEAD de IA - SQLAlchemy Models
Ativos de IA, tarefas diárias, licenças, indicadores/KPIs e base de conhecimento.

As tabelas usam colunas String simples (em vez de Enum nativo) para garantir
portabilidade entre SQLite (dev) e PostgreSQL/Supabase (produção) sem migração de tipos.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, func, Index
from database import Base


class Asset(Base):
    """Ativo de IA sob gestão do HEAD (modelo, agente, automação, integração, dataset, infra)."""
    __tablename__ = "head_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    asset_type = Column(String(40), nullable=False, default="Modelo LLM")  # Modelo LLM | Agente | Automação | Integração | Dataset | Infraestrutura
    vendor = Column(String(80), default="")
    owner = Column(String(120), default="")           # responsável técnico
    status = Column(String(30), nullable=False, default="Ativo")  # Ativo | Em avaliação | Descontinuado
    environment = Column(String(30), default="Produção")  # Produção | Homologação | Desenvolvimento
    criticality = Column(String(20), default="Média")     # Baixa | Média | Alta | Crítica
    monthly_cost = Column(Float, default=0.0)
    description = Column(Text, default="")
    acquisition_date = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DailyTask(Base):
    """Tarefa realizada no dia a dia da operação de IA."""
    __tablename__ = "head_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    responsible = Column(String(120), default="")
    category = Column(String(60), default="Operação")
    status = Column(String(30), nullable=False, default="Pendente")   # Pendente | Em andamento | Concluída | Bloqueada
    priority = Column(String(20), nullable=False, default="Média")    # Baixa | Média | Alta | Crítica
    task_date = Column(String(10), nullable=False, default="", index=True)
    hours_spent = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_head_tasks_date_status", "task_date", "status"),
    )


class License(Base):
    """Licença de software/serviço de IA sob controle do HEAD."""
    __tablename__ = "head_licenses"

    id = Column(Integer, primary_key=True, index=True)
    software = Column(String(150), nullable=False, index=True)
    vendor = Column(String(80), default="")
    plan = Column(String(80), default="")
    seats_total = Column(Integer, default=0)
    seats_used = Column(Integer, default=0)
    monthly_cost = Column(Float, default=0.0)
    status = Column(String(30), nullable=False, default="Ativa")  # Ativa | Em renovação | Expirada | Cancelada
    renewal_date = Column(String(10), default="")
    owner = Column(String(120), default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Indicator(Base):
    """Indicador / KPI mensal do HEAD de IA."""
    __tablename__ = "head_indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(60), default="Operacional")  # Operacional | Financeiro | Adoção | Qualidade | Risco
    period = Column(String(7), nullable=False, default="", index=True)  # YYYY-MM
    unit = Column(String(20), default="")                 # %, R$, h, un, ...
    target = Column(Float, default=0.0)
    actual = Column(Float, default=0.0)
    trend = Column(String(20), default="Estável")         # Subindo | Estável | Caindo
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_head_indicators_period_cat", "period", "category"),
    )


class ProcessImprovement(Base):
    """Iniciativa de otimização de processo interno (fluxo PDCA/Kaizen)."""
    __tablename__ = "head_processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    area = Column(String(80), default="")
    owner = Column(String(120), default="")           # dono do processo
    stage = Column(String(20), nullable=False, default="Mapeamento")  # Mapeamento | Diagnóstico | Priorização | Redesenho | Implementação | Medição | Padronizado
    status = Column(String(20), nullable=False, default="Em andamento")  # Em andamento | Concluído | Pausado
    impact = Column(String(10), default="Médio")      # Baixo | Médio | Alto  (matriz)
    effort = Column(String(10), default="Médio")      # Baixo | Médio | Alto  (matriz)
    ai_automation = Column(String(10), default="Não")  # Não | Parcial | Total (grau de automação com IA)
    problem = Column(Text, default="")                # situação atual / gargalo (as-is)
    proposal = Column(Text, default="")               # proposta otimizada (to-be)
    time_before = Column(Float, default=0.0)          # horas/ciclo antes
    time_after = Column(Float, default=0.0)           # horas/ciclo depois
    cost_before = Column(Float, default=0.0)          # custo mensal antes
    cost_after = Column(Float, default=0.0)           # custo mensal depois
    responsible = Column(String(120), default="")     # responsável pela implementação
    due_date = Column(String(10), default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_head_processes_stage_status", "stage", "status"),
    )


class KnowledgeArticle(Base):
    """Artigo da base de conhecimento do HEAD de IA."""
    __tablename__ = "head_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    category = Column(String(60), default="Geral")
    summary = Column(String(300), default="")
    content = Column(Text, default="")
    tags = Column(String(200), default="")   # separadas por vírgula
    author = Column(String(120), default="")
    status = Column(String(20), nullable=False, default="Publicado")  # Rascunho | Publicado | Arquivado
    updated_date = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Activity(Base):
    """Atividade agregada das ferramentas do Head (Jira, Drive, GitHub)."""
    __tablename__ = "head_activities"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(20), nullable=False, index=True)   # Jira | Drive | GitHub
    title = Column(String(300), nullable=False)
    reference = Column(String(60), default="")                # SCRUM-50, PR #49...
    category = Column(String(120), default="")                # projeto / pasta / repo
    status = Column(String(40), default="")
    priority = Column(String(20), default="")
    url = Column(Text, default="")
    activity_date = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SyncState(Base):
    """Estado da última sincronização automática por fonte (Jira, Drive, Gmail)."""
    __tablename__ = "head_sync_state"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(20), nullable=False, unique=True, index=True)  # Jira | Drive | Gmail
    status = Column(String(30), default="")   # ok | erro | não configurado
    last_count = Column(Integer, default=0)
    message = Column(String(300), default="")
    last_run = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PurchaseRequest(Base):
    """Solicitação de compra (importada dos e-mails) para o controle de licenças."""
    __tablename__ = "head_purchase_requests"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String(250), nullable=False)
    vendor = Column(String(80), default="")
    requester = Column(String(120), default="")
    cost_center = Column(String(80), default="")
    amount = Column(String(60), default="")          # "US$ 20,00" / "R$ 246,67"
    status = Column(String(30), default="Solicitado")  # Solicitado | Aprovado | Pago | Recusado
    approver = Column(String(120), default="")
    request_date = Column(String(10), default="")
    due_date = Column(String(10), default="")
    source = Column(String(40), default="E-mail")     # E-mail | Formulário
    url = Column(Text, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

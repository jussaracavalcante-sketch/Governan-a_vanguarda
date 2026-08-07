"""
VANGUARDIAN - Governance module
Modelos, schemas, CRUD e rotas que espelham as telas do protótipo:
Portfólio de clientes, Stack & homologação, Biblioteca de prompts,
Pessoas & skills, Visão executiva (iniciativas/indicadores) e
Compliance & auditoria (ocorrências, trilha de auditoria, observabilidade).
"""
from datetime import datetime, timedelta, timezone
import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func
from sqlalchemy.orm import Session

from database import Base, get_db
from auth.dependencies import get_current_user
from models import User, AuditLog


# ─────────────────────────── MODELS ───────────────────────────
class Client(Base):
    __tablename__ = "gov_clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    segment = Column(String(160), default="")
    squad = Column(String(80), default="")
    ai_usage = Column(String(80), default="")          # ex.: "Playbook ativo", "7 fluxos"
    brand_safety = Column(String(120), default="")
    responsible = Column(String(120), default="")
    stage = Column(String(20), default="active")        # active | onboarding | at-risk
    flows = Column(Integer, default=0)
    playbook_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StackTool(Base):
    __tablename__ = "gov_stack_tools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    description = Column(String(240), default="")
    status = Column(String(30), default="Em análise")   # Homologada | Em análise | Restrita | Reprovada
    request_code = Column(String(40), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PromptItem(Base):
    __tablename__ = "gov_prompts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(400), default="")
    area = Column(String(60), default="")
    control = Column(String(30), default="Revisão pendente")  # Aprovado | Revisão pendente | Reprovado
    content = Column(Text, default="")
    repo_url = Column(String(300), default="")
    last_review = Column(String(30), default="")
    uses = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SkillItem(Base):
    __tablename__ = "gov_skills"
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(120), nullable=False)
    description = Column(String(240), default="")
    level = Column(String(30), default="Intermediário")  # Iniciante|Intermediário|Avançado|Especialista|Prioridade
    reviewer = Column(String(120), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TrainingTrack(Base):
    __tablename__ = "gov_training"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    percent = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Initiative(Base):
    __tablename__ = "gov_initiatives"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    area = Column(String(200), default="")
    status = Column(String(40), default="Em validação")  # Em validação|Em produção|Risco: dados|Em homologação
    hours_saved = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdoptionArea(Base):
    __tablename__ = "gov_adoption"
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(120), nullable=False)
    percent = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Incident(Base):
    __tablename__ = "gov_incidents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    area = Column(String(120), default="")
    criticality = Column(String(20), default="Baixa")   # Baixa|Média|Alta|Crítica
    status = Column(String(30), default="Em análise")   # Conforme|Em análise|Ação necessária
    description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────── SCHEMAS ───────────────────────────
class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ClientIn(BaseModel):
    name: str
    segment: str = ""
    squad: str = ""
    ai_usage: str = ""
    brand_safety: str = ""
    responsible: str = ""
    stage: str = "active"
    flows: int = 0
    playbook_active: bool = False


class StackToolIn(BaseModel):
    name: str
    description: str = ""
    status: str = "Em análise"
    request_code: str = ""


class PromptItemIn(BaseModel):
    title: str
    description: str = ""
    area: str = ""
    control: str = "Revisão pendente"
    content: str = ""
    repo_url: str = ""
    last_review: str = ""
    uses: int = 0


class SkillItemIn(BaseModel):
    area: str
    description: str = ""
    level: str = "Intermediário"
    reviewer: str = ""


class InitiativeIn(BaseModel):
    name: str
    area: str = ""
    status: str = "Em validação"
    hours_saved: int = 0


class IncidentIn(BaseModel):
    title: str
    area: str = ""
    criticality: str = "Baixa"
    status: str = "Em análise"
    description: str = ""


# ─────────────────────────── ROUTER ───────────────────────────
router = APIRouter(prefix="/governance", tags=["Governança"])

_MODELS = {
    "clients": Client, "stack": StackTool, "prompts": PromptItem,
    "skills": SkillItem, "initiatives": Initiative, "incidents": Incident,
}


def _audit(db: Session, user: User, action: str, resource: str, rid: int, details: dict):
    db.add(AuditLog(
        user_id=user.id, user_email=user.email, action=action,
        resource_type=resource, resource_id=rid,
        details=json.dumps(details, ensure_ascii=False), success=True,
    ))
    db.commit()


def _serialize(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _list(db, model):
    return [_serialize(o) for o in db.query(model).order_by(model.id).all()]


# ---- Portfólio de clientes ----
@router.get("/clients")
def list_clients(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, Client)


@router.post("/clients", status_code=201)
def create_client(item: ClientIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = Client(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "client", obj.id, {"name": obj.name})
    return _serialize(obj)


# ---- Stack & homologação ----
@router.get("/stack")
def list_stack(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, StackTool)


@router.post("/stack", status_code=201)
def create_stack(item: StackToolIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = StackTool(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "tool", obj.id, {"name": obj.name})
    return _serialize(obj)


# ---- Biblioteca de prompts ----
@router.get("/prompts")
def list_prompts(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, PromptItem)


@router.post("/prompts", status_code=201)
def create_prompt(item: PromptItemIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = PromptItem(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "prompt", obj.id, {"title": obj.title})
    return _serialize(obj)


# ---- Pessoas & skills ----
@router.get("/skills")
def list_skills(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, SkillItem)


@router.post("/skills", status_code=201)
def create_skill(item: SkillItemIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = SkillItem(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "skill", obj.id, {"area": obj.area})
    return _serialize(obj)


@router.get("/training")
def list_training(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, TrainingTrack)


# ---- Visão executiva (iniciativas + adoção) ----
@router.get("/initiatives")
def list_initiatives(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, Initiative)


@router.post("/initiatives", status_code=201)
def create_initiative(item: InitiativeIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = Initiative(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "initiative", obj.id, {"name": obj.name})
    return _serialize(obj)


@router.get("/adoption")
def list_adoption(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, AdoptionArea)


# ---- Compliance & ocorrências ----
@router.get("/incidents")
def list_incidents(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, Incident)


@router.post("/incidents", status_code=201)
def create_incident(item: IncidentIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = Incident(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "incident", obj.id, {"title": obj.title, "criticality": obj.criticality})
    return _serialize(obj)


# ---- Indicadores (KPIs dos painéis) ----
@router.get("/overview")
def overview(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    clients = db.query(Client).all()
    tools = db.query(StackTool).all()
    inits = db.query(Initiative).all()
    incidents = db.query(Incident).all()
    homolog = [t for t in tools if t.status == "Homologada"]
    since = datetime.now(timezone.utc) - timedelta(days=30)
    audits_month = db.query(AuditLog).filter(AuditLog.timestamp >= since).count()
    pendencias = [i for i in incidents if i.status != "Conforme"]
    return {
        "dashboard": {
            "clientes_governados": len(clients),
            "playbooks_ativos": len([c for c in clients if c.playbook_active]),
            "horas_economizadas": sum(i.hours_saved for i in inits),
            "fluxos_automatizados": sum(c.flows for c in clients),
            "fluxos_homologacao": len([i for i in inits if "homolog" in (i.status or "").lower()]),
            "conformidade_ia": round(100 * len(homolog) / len(tools)) if tools else 0,
            "roi_estimado": 3.4,
            "adocao_ativa": 82,
        },
        "compliance": {
            "auditorias_mes": audits_month,
            "pendencias_abertas": len(pendencias),
            "pendencias_baixas": len([i for i in pendencias if i.criticality in ("Baixa", "Média")]),
            "saidas_revisadas": 97,
            "incidentes_criticos": len([i for i in incidents if i.criticality == "Crítica"]),
        },
    }


# ---- Trilha de auditoria ----
@router.get("/audit")
def audit_trail(limit: int = 20, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    rows = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [{
        "id": r.id,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        "user_email": r.user_email,
        "action": r.action,
        "resource_type": r.resource_type,
        "resource_id": r.resource_id,
        "success": r.success,
        "details": r.details,
    } for r in rows]


# ---- Observabilidade ----
@router.get("/observability")
def observability(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    return {
        "status": "operational",
        "db": "ok",
        "total_audit_events": db.query(AuditLog).count(),
        "events_24h": db.query(AuditLog).filter(AuditLog.timestamp >= since).count(),
        "clients": db.query(Client).count(),
        "prompts": db.query(PromptItem).count(),
        "incidents_open": db.query(Incident).filter(Incident.status != "Conforme").count(),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────── SEED ───────────────────────────
def seed_governance(db: Session):
    if db.query(Client).first():
        return
    db.add_all([
        Client(name="Vanguarda Institucional", segment="Conhecimento corporativo", squad="Estratégia",
               ai_usage="Playbook ativo", brand_safety="Revisão obrigatória", responsible="Diretoria de IA",
               stage="active", flows=0, playbook_active=True),
        Client(name="Conta Atlas", segment="Performance & conteúdo", squad="Growth",
               ai_usage="7 fluxos", brand_safety="Dados internos", responsible="Account Lead",
               stage="active", flows=7, playbook_active=True),
        Client(name="Conta Aurora", segment="Social & audiovisual", squad="Criação",
               ai_usage="Em onboarding", brand_safety="Validação de imagem", responsible="Creative Lead",
               stage="onboarding", flows=0, playbook_active=False),
        Client(name="Conta Nexo", segment="Comercial B2B", squad="Comercial",
               ai_usage="1 pendência", brand_safety="Dados confidenciais", responsible="Sales Ops",
               stage="at-risk", flows=0, playbook_active=False),
    ])
    db.add_all([
        StackTool(name="ChatGPT Enterprise", description="Texto, análise e automação assistida", status="Homologada"),
        StackTool(name="Adobe Firefly", description="Imagem e criação com revisão autoral", status="Homologada"),
        StackTool(name="Make / APIs", description="Integrações e automações operacionais", status="Homologada"),
        StackTool(name="Ferramenta externa de vídeo", description="Solicitação #VG-204", status="Em análise", request_code="VG-204"),
    ])
    db.add_all([
        PromptItem(title="Briefing estratégico 360°", description="Transforma demanda em contexto, objetivos e critérios de entrega.",
                   area="Planejamento", control="Aprovado", last_review="04 ago 2026", uses=86),
        PromptItem(title="Legendas com voz de marca", description="Gera variações com tom, persona e restrições do cliente.",
                   area="Social", control="Aprovado", last_review="02 ago 2026", uses=143),
        PromptItem(title="Insight de performance semanal", description="Converte dados de mídia em decisões acionáveis.",
                   area="Mídia", control="Revisão pendente", last_review="28 jul 2026", uses=48),
    ])
    db.add_all([
        SkillItem(area="Criação", description="Ideação, imagem, vídeo e revisão criativa", level="Avançado"),
        SkillItem(area="Planejamento & Estratégia", description="Research, personas, SWOT e propostas", level="Avançado"),
        SkillItem(area="Atendimento", description="Briefing, atas, cronogramas e SLA", level="Intermediário"),
        SkillItem(area="Financeiro & RH", description="Processos sensíveis e dados restritos", level="Prioridade"),
    ])
    db.add_all([
        TrainingTrack(name="Fundamentos e uso responsável", percent=100),
        TrainingTrack(name="Segurança e LGPD", percent=88),
        TrainingTrack(name="Engenharia de prompts", percent=76),
        TrainingTrack(name="Automação por área", percent=54),
    ])
    db.add_all([
        Initiative(name="Padronização de briefs inteligentes", area="Atendimento + Planejamento + Criação", status="Em validação", hours_saved=0),
        Initiative(name="Agente de performance para mídia paga", area="Dados + Mídia · conexão de métricas e insights", status="Em produção", hours_saved=318),
        Initiative(name="Base de conhecimento de marca", area="Brand book, tom de voz e restrições por cliente", status="Risco: dados", hours_saved=0),
        Initiative(name="Automação de relatórios executivos", area="BI + Account Management", status="Em homologação", hours_saved=0),
    ])
    db.add_all([
        AdoptionArea(area="Criação & Conteúdo", percent=91),
        AdoptionArea(area="Atendimento", percent=84),
        AdoptionArea(area="Mídia & Performance", percent=78),
        AdoptionArea(area="Comercial", percent=66),
    ])
    db.add_all([
        Incident(title="Biblioteca de prompts - revisão de versão", area="Planejamento", criticality="Baixa", status="Conforme"),
        Incident(title="Solicitação de ferramenta externa", area="Criação", criticality="Média", status="Em análise"),
        Incident(title="Uso de dados confidenciais fora do fluxo", area="Conta Nexo", criticality="Alta", status="Ação necessária"),
    ])
    db.commit()

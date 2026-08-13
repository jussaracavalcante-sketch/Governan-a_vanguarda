"""
PrMO - Governance module
Modelos, schemas, CRUD e rotas que espelham as telas do protótipo:
Portfólio de clientes, Stack & homologação, Biblioteca de prompts,
Pessoas & skills, Visão executiva (iniciativas/indicadores) e
Compliance & auditoria (ocorrências, trilha de auditoria, observabilidade).
"""
from datetime import datetime, timedelta, timezone
import json
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Float, func
from sqlalchemy.orm import Session

from database import Base, get_db
from auth.dependencies import get_current_user, get_current_manager_user
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
    cost_per_call = Column(Float, default=0.0)
    last_review = Column(String(30), default="")
    uses = Column(Integer, default=0)
    # --- Padrão corporativo NIA-001 (Engenharia de Prompts) ---
    code = Column(String(40), default="", index=True)   # Nomenclatura PROMPT-ÁREA-NNN (NIA-001 §7)
    version = Column(String(10), default="1.0")          # Versionamento (NIA-001 §8)
    ptype = Column(String(1), default="")                # Classificação A|B|C|D|E (NIA-001 §6)
    tool = Column(String(80), default="")                # Ferramenta utilizada (NIA-001 §5)
    author = Column(String(120), default="")             # Autor/responsável (NIA-001 §9)
    data_class = Column(String(20), default="")          # Classificação da informação (Política §7)
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


class CostPolicy(Base):
    __tablename__ = "gov_cost_policy"
    id = Column(Integer, primary_key=True, index=True)
    max_cost_per_call = Column(Float, default=0.50)   # teto de custo por chamada
    currency = Column(String(8), default="BRL")
    updated_by = Column(String(120), default="")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RegistryRecord(Base):
    """Registros migrados (Governança IA — 30 dias), anonimizados."""
    __tablename__ = "gov_registry"
    id = Column(Integer, primary_key=True, index=True)
    registry = Column(String(30), index=True)   # asset|risk|knowledge|opportunity|diagnostic|plan30
    code = Column(String(255), default="")       # id/indicador do registro (rótulos de diagnóstico podem ser longos)
    data = Column(Text, default="{}")            # JSON do registro (sem dados pessoais)
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


class SupportTicket(Base):
    """Suporte técnico / canal de comunicação: reportes de uso indevido da IA,
    solicitações e canal dos embaixadores de IA."""
    __tablename__ = "gov_support"
    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(30), default="Solicitação")     # Uso indevido | Solicitação | Embaixadores
    subject = Column(String(200), nullable=False)
    area = Column(String(120), default="")
    severity = Column(String(20), default="Média")        # Baixa|Média|Alta|Crítica (uso indevido)
    message = Column(Text, default="")
    requester = Column(String(120), default="")           # nome do solicitante
    requester_email = Column(String(120), default="", index=True)
    status = Column(String(30), default="Aberto")         # Aberto|Em atendimento|Resolvido|Fechado
    response = Column(Text, default="")
    handled_by = Column(String(120), default="")
    handled_at = Column(String(30), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssetRequest(Base):
    """Solicitação de cadastro de um novo ativo digital de IA (aplicação/agente)."""
    __tablename__ = "gov_asset_requests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)            # nome completo do ativo/aplicação
    features = Column(Text, default="")                    # funcionalidades da aplicação
    url = Column(String(300), default="")                  # URL da aplicação
    repo_url = Column(String(300), default="")             # repositório
    repo_scope = Column(String(20), default="Público")     # Público | Institucional
    requester = Column(String(120), default="")
    requester_email = Column(String(120), default="", index=True)
    status = Column(String(20), default="Pendente")        # Pendente | Aprovado | Reprovado
    review_note = Column(Text, default="")
    handled_by = Column(String(120), default="")
    handled_at = Column(String(30), default="")
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
    cost_per_call: float = 0.0
    last_review: str = ""
    uses: int = 0
    # Padrão NIA-001 (todos opcionais no envio; o backend completa código/autor/versão)
    code: str = ""
    version: str = "1.0"
    ptype: str = ""
    tool: str = ""
    author: str = ""
    data_class: str = ""


class PromptUpdateIn(BaseModel):
    """Edição de prompt (todos os campos opcionais; só os enviados são alterados)."""
    title: str | None = None
    description: str | None = None
    area: str | None = None
    content: str | None = None
    repo_url: str | None = None
    cost_per_call: float | None = None
    tool: str | None = None
    ptype: str | None = None
    data_class: str | None = None
    version: str | None = None


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


class SupportTicketIn(BaseModel):
    kind: str = "Solicitação"          # Uso indevido | Solicitação | Embaixadores
    subject: str
    area: str = ""
    severity: str = "Média"
    message: str = ""


class SupportUpdateIn(BaseModel):
    status: str | None = None          # Aberto | Em atendimento | Resolvido | Fechado
    response: str | None = None


class AssetRequestIn(BaseModel):
    name: str                           # nome completo
    features: str = ""                  # funcionalidades da aplicação
    url: str = ""
    repo_url: str = ""
    repo_scope: str = "Público"         # Público | Institucional


class AssetReviewIn(BaseModel):
    decision: str                       # Aprovado | Reprovado
    note: str | None = None


class HomologacaoIn(BaseModel):
    decision: str  # "Aprovado" | "Reprovado"


class CostPolicyIn(BaseModel):
    max_cost_per_call: float
    currency: str = "BRL"


def get_or_create_policy(db: Session) -> CostPolicy:
    pol = db.query(CostPolicy).first()
    if not pol:
        pol = CostPolicy(max_cost_per_call=0.50, currency="BRL")
        db.add(pol); db.commit(); db.refresh(pol)
    return pol


_MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _hoje_pt() -> str:
    d = datetime.now(timezone.utc)
    return f"{d.day:02d} {_MESES[d.month - 1]} {d.year}"


# ── Padrão corporativo NIA-001 (Engenharia de Prompts) ──────────────────────
# Nomenclatura PROMPT-ÁREA-NNN (§7). Mapa de sigla por macroárea; fallback = 3 letras.
_AREA_CODE = {
    "criação": "CRI", "criacao": "CRI", "criação & conteúdo": "CRI", "conteúdo": "CRI",
    "atendimento": "ATD", "account": "ATD",
    "planejamento": "PLA", "planejamento & estratégia": "PLA", "estratégia": "PLA",
    "mídia": "MID", "midia": "MID", "mídia & performance": "MID", "performance": "MID",
    "social": "SOC", "social media": "SOC",
    "comercial": "CML", "vendas": "CML",
    "inbound": "INB", "rh": "RH", "recursos humanos": "RH",
    "financeiro": "FIN", "financeiro & rh": "FIN", "administrativo": "ADM",
    "desenvolvimento": "DEV", "diretoria": "CEO", "gestão de projetos": "PMO",
    "dados": "DAT", "conhecimento": "KNW",
}


def _area_prefix(area: str) -> str:
    a = (area or "").strip().lower()
    if a in _AREA_CODE:
        return _AREA_CODE[a]
    for key, sig in _AREA_CODE.items():
        if key in a:
            return sig
    base = "".join(ch for ch in a if ch.isalnum())
    return (base[:3] or "GEN").upper()


def _ptype_from(text: str) -> str:
    """Classifica o tipo (A operacional | B analítico | C estratégico | D automação |
    E criativo) a partir de palavras-chave do Tipo/Área/Título — NIA-001 §6."""
    t = (text or "").lower()
    def has(*words): return any(w in t for w in words)
    if has("automa", "fluxo", "api", "agente", "integra", "webhook"):
        return "D"
    if has("planejamento", "estrat", "roadmap", "plano diretor", "consultoria", "diretoria"):
        return "C"
    if has("benchmark", "swot", "indicador", "kpi", "análise", "analise", "analítico", "forecast", "dados"):
        return "B"
    if has("campanha", "roteiro", "storytelling", "design", "naming", "criativ", "copy", "conteúdo", "social", "vídeo", "video", "imagem"):
        return "E"
    return "A"


def _next_prompt_code(db: Session, area: str) -> str:
    pref = _area_prefix(area)
    like = f"PROMPT-{pref}-%"
    n = db.query(PromptItem).filter(PromptItem.code.like(like)).count()
    return f"PROMPT-{pref}-{n + 1:03d}"


# ── Regras de negócio (derivadas das normas corporativas) ───────────────────
import re

# R1 — Proibições de segurança/LGPD (NIA-001 §13 / Política §6): segredos e PII.
_FORBIDDEN_PATTERNS = [
    (r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "CPF"),
    (r"\b\d{4}[ .-]?\d{4}[ .-]?\d{4}[ .-]?\d{4}\b", "cartão de crédito"),
    (r"(?i)\b(senha|password|api[_ -]?key|secret|client_secret|token|bearer)\b\s*[:=]\s*\S+", "credencial/segredo"),
    (r"(?i)\b(burlar|sonegar|fraude|fraudar)\b", "conteúdo vedado (fraude/burla)"),
]

# R4 — Repositórios "externos" (serviços fora do ambiente corporativo).
_EXTERNAL_REPO_HOSTS = ("github.com", "gitlab.com", "bitbucket.org", "drive.google.com", "dropbox.com")

# Catálogo público das regras (para /governance/rules, frontend e auditoria).
BUSINESS_RULES = [
    {"id": "R1", "base": "NIA-001 §13 / Política §6", "quando": "cadastro",
     "regra": "Prompt não pode conter credenciais, segredos ou dados pessoais (CPF, cartão)."},
    {"id": "R2", "base": "Política §4", "quando": "homologação",
     "regra": "Só homologa (Aprovado) prompt cuja ferramenta esteja Homologada no stack."},
    {"id": "R3", "base": "NIA-001 §5/§12", "quando": "homologação",
     "regra": "Aprovação exige metadados mínimos: código, objetivo/descrição e conteúdo."},
    {"id": "R4", "base": "Política §7", "quando": "cadastro/homologação",
     "regra": "Dado classificado como Restrito não pode ter repositório público externo."},
]


def check_forbidden(*texts: str) -> list[str]:
    """R1: retorna as categorias proibidas encontradas no texto do prompt."""
    blob = " \n ".join(t for t in texts if t)
    hits = []
    for pat, label in _FORBIDDEN_PATTERNS:
        if re.search(pat, blob):
            hits.append(label)
    return hits


def _repo_is_external(url: str) -> bool:
    u = (url or "").lower()
    return any(h in u for h in _EXTERNAL_REPO_HOSTS)


def validate_prompt_intake(data: dict) -> list[str]:
    """Regras aplicadas no cadastro (R1, R4). Retorna lista de violações."""
    problems = []
    forb = check_forbidden(data.get("title", ""), data.get("description", ""), data.get("content", ""))
    if forb:
        problems.append("R1: conteúdo proibido — " + ", ".join(sorted(set(forb))))
    if str(data.get("data_class", "")).strip().lower() == "restrito" and _repo_is_external(data.get("repo_url", "")):
        problems.append("R4: dado 'Restrito' não pode apontar para repositório público externo")
    return problems


def validate_prompt_approval(obj: "PromptItem", db: Session) -> list[str]:
    """Regras aplicadas na homologação-Aprovado (R1–R4). Retorna lista de violações."""
    problems = validate_prompt_intake({
        "title": obj.title, "description": obj.description, "content": obj.content,
        "data_class": obj.data_class, "repo_url": obj.repo_url,
    })
    # R3 — metadados mínimos
    faltas = [n for n, v in (("código", obj.code), ("objetivo/descrição", obj.description), ("conteúdo", obj.content)) if not (v or "").strip()]
    if faltas:
        problems.append("R3: preencha antes de aprovar — " + ", ".join(faltas))
    # R2 — ferramenta homologada
    tool = (obj.tool or "").strip()
    if not tool:
        problems.append("R2: informe a ferramenta utilizada (deve ser homologada)")
    else:
        homolog = db.query(StackTool).filter(StackTool.status == "Homologada").all()
        nomes = [t.name.lower() for t in homolog]
        if not any(tool.lower() in n or n in tool.lower() for n in nomes):
            problems.append(f"R2: ferramenta '{tool}' não está homologada no stack")
    return problems


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
def create_client(item: ClientIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    obj = Client(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "client", obj.id, {"name": obj.name})
    return _serialize(obj)


# ---- Stack & homologação ----
@router.get("/stack")
def list_stack(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, StackTool)


@router.post("/stack", status_code=201)
def create_stack(item: StackToolIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
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
    data = item.model_dump()
    role = str(getattr(u.role, "value", u.role))
    # R1/R4 — regras de cadastro (segurança/LGPD e classificação da informação).
    violacoes = validate_prompt_intake(data)
    if violacoes:
        _audit(db, u, "REJECT", "prompt", 0, {"title": data.get("title"), "violacoes": violacoes})
        raise HTTPException(status_code=422, detail={"regras": violacoes})
    # Colaborador (User) só envia para validação: status sempre "Revisão pendente".
    # A homologação (Aprovado/Reprovado) é exclusiva de Manager/Admin.
    if role not in ("Admin", "Manager"):
        data["control"] = "Revisão pendente"
    # Padrão NIA-001: completa metadados obrigatórios se não vierem preenchidos.
    if not data.get("code"):
        data["code"] = _next_prompt_code(db, data.get("area", ""))
    if not data.get("ptype"):
        data["ptype"] = _ptype_from(f"{data.get('area','')} {data.get('title','')} {data.get('description','')}")
    if not data.get("author"):
        data["author"] = u.name or u.email
    if not data.get("version"):
        data["version"] = "1.0"
    if not data.get("data_class"):
        data["data_class"] = "Uso interno"
    obj = PromptItem(**data)
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "prompt", obj.id,
           {"title": obj.title, "code": obj.code, "control": obj.control, "by_role": role})
    return _serialize(obj)


@router.post("/prompts/{pid}/homologar")
def homologar_prompt(pid: int, item: HomologacaoIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    if item.decision not in ("Aprovado", "Reprovado"):
        raise HTTPException(status_code=422, detail="decision deve ser 'Aprovado' ou 'Reprovado'")
    obj = db.query(PromptItem).filter(PromptItem.id == pid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    # R1–R4 — regras de homologação (só bloqueiam a APROVAÇÃO; reprovar é sempre permitido).
    if item.decision == "Aprovado":
        violacoes = validate_prompt_approval(obj, db)
        if violacoes:
            _audit(db, u, "REJECT", "prompt", obj.id, {"title": obj.title, "violacoes": violacoes})
            raise HTTPException(status_code=422, detail={"regras": violacoes})
    obj.control = item.decision
    obj.last_review = _hoje_pt()
    db.commit(); db.refresh(obj)
    _audit(db, u, "APPROVE" if item.decision == "Aprovado" else "REJECT", "prompt", obj.id,
           {"title": obj.title, "control": obj.control})
    return _serialize(obj)


@router.put("/prompts/{pid}")
def update_prompt(pid: int, item: PromptUpdateIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    obj = db.query(PromptItem).filter(PromptItem.id == pid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    data = item.model_dump(exclude_unset=True)
    if "ptype" in data and data["ptype"]:
        data["ptype"] = str(data["ptype"]).strip()[:1]
    # R1/R4 sobre o resultado mesclado (segurança/LGPD e classificação).
    merged = {"title": obj.title, "description": obj.description, "content": obj.content,
              "data_class": obj.data_class, "repo_url": obj.repo_url, **data}
    violacoes = validate_prompt_intake(merged)
    if violacoes:
        _audit(db, u, "REJECT", "prompt", obj.id, {"title": merged.get("title"), "violacoes": violacoes})
        raise HTTPException(status_code=422, detail={"regras": violacoes})
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    _audit(db, u, "UPDATE", "prompt", obj.id, {"title": obj.title, "campos": list(data.keys())})
    return _serialize(obj)


# ---- Regras de negócio (catálogo derivado das normas corporativas) ----
@router.get("/rules")
def list_rules(u: User = Depends(get_current_user)):
    return {"regras": BUSINESS_RULES}


# ---- Suporte técnico / canal de comunicação ----
_SUPPORT_KINDS = ("Uso indevido", "Solicitação", "Embaixadores")


@router.post("/support", status_code=201)
def create_support(item: SupportTicketIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Abre um chamado: reporte de uso indevido, solicitação ou mensagem de embaixador.
    Aberto a qualquer colaborador autenticado."""
    kind = item.kind if item.kind in _SUPPORT_KINDS else "Solicitação"
    # R1 (LGPD/segurança): não permitir credenciais/segredos/PII no texto do chamado.
    forb = check_forbidden(item.subject, item.message)
    if forb:
        raise HTTPException(status_code=422, detail={"regras": ["R1: conteúdo proibido — " + ", ".join(sorted(set(forb)))]})
    obj = SupportTicket(
        kind=kind, subject=item.subject.strip()[:200], area=item.area.strip()[:120],
        severity=(item.severity or "Média"), message=item.message.strip(),
        requester=(u.name or u.email), requester_email=u.email, status="Aberto",
    )
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "support", obj.id, {"kind": kind, "subject": obj.subject})
    return _serialize(obj)


@router.get("/support")
def list_support(kind: str = "", status: str = "", db: Session = Depends(get_db),
                 u: User = Depends(get_current_manager_user)):
    """Fila de atendimento (controlador): todos os chamados, com filtros opcionais."""
    q = db.query(SupportTicket)
    if kind:
        q = q.filter(SupportTicket.kind == kind)
    if status:
        q = q.filter(SupportTicket.status == status)
    return [_serialize(o) for o in q.order_by(SupportTicket.id.desc()).all()]


@router.get("/support/mine")
def my_support(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Chamados abertos pelo próprio colaborador."""
    rows = (db.query(SupportTicket)
            .filter(SupportTicket.requester_email == u.email)
            .order_by(SupportTicket.id.desc()).all())
    return [_serialize(o) for o in rows]


@router.put("/support/{sid}")
def update_support(sid: int, item: SupportUpdateIn, db: Session = Depends(get_db),
                   u: User = Depends(get_current_manager_user)):
    """Atendimento do chamado (controlador): muda status e/ou registra resposta."""
    obj = db.query(SupportTicket).filter(SupportTicket.id == sid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if item.status is not None:
        obj.status = item.status
    if item.response is not None:
        obj.response = item.response
    obj.handled_by = u.name or u.email
    obj.handled_at = _hoje_pt()
    db.commit(); db.refresh(obj)
    _audit(db, u, "UPDATE", "support", obj.id, {"status": obj.status})
    return _serialize(obj)


# ---- Solicitação de cadastro de novo ativo digital de IA ----
@router.post("/asset-requests", status_code=201)
def create_asset_request(item: AssetRequestIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Qualquer colaborador solicita o cadastro de um novo ativo digital de IA.
    Entra como 'Pendente' para triagem/homologação do controlador."""
    forb = check_forbidden(item.name, item.features, item.url, item.repo_url)
    if forb:
        raise HTTPException(status_code=422, detail={"regras": ["R1: conteúdo proibido — " + ", ".join(sorted(set(forb)))]})
    scope = item.repo_scope if item.repo_scope in ("Público", "Institucional") else "Público"
    obj = AssetRequest(
        name=item.name.strip()[:200], features=item.features.strip(),
        url=item.url.strip()[:300], repo_url=item.repo_url.strip()[:300], repo_scope=scope,
        requester=(u.name or u.email), requester_email=u.email, status="Pendente",
    )
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "asset_request", obj.id, {"name": obj.name, "scope": scope})
    return _serialize(obj)


@router.get("/asset-requests")
def list_asset_requests(status: str = "", db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    q = db.query(AssetRequest)
    if status:
        q = q.filter(AssetRequest.status == status)
    return [_serialize(o) for o in q.order_by(AssetRequest.id.desc()).all()]


@router.get("/asset-requests/mine")
def my_asset_requests(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    rows = (db.query(AssetRequest).filter(AssetRequest.requester_email == u.email)
            .order_by(AssetRequest.id.desc()).all())
    return [_serialize(o) for o in rows]


@router.put("/asset-requests/{rid}")
def review_asset_request(rid: int, item: AssetReviewIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    if item.decision not in ("Aprovado", "Reprovado", "Pendente"):
        raise HTTPException(status_code=422, detail="decision deve ser 'Aprovado', 'Reprovado' ou 'Pendente'")
    obj = db.query(AssetRequest).filter(AssetRequest.id == rid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    obj.status = item.decision
    if item.note is not None:
        obj.review_note = item.note
    obj.handled_by = u.name or u.email
    obj.handled_at = _hoje_pt()
    db.commit(); db.refresh(obj)
    _audit(db, u, "APPROVE" if item.decision == "Aprovado" else ("REJECT" if item.decision == "Reprovado" else "UPDATE"),
           "asset_request", obj.id, {"name": obj.name, "status": obj.status})
    return _serialize(obj)


# ---- Política de custo (teto por chamada, controlado pelo PrMO) ----
@router.get("/cost-policy")
def get_cost_policy(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _serialize(get_or_create_policy(db))


@router.put("/cost-policy")
def update_cost_policy(item: CostPolicyIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    pol = get_or_create_policy(db)
    pol.max_cost_per_call = item.max_cost_per_call
    pol.currency = item.currency
    pol.updated_by = u.email
    db.commit(); db.refresh(pol)
    _audit(db, u, "UPDATE", "cost_policy", pol.id,
           {"max_cost_per_call": pol.max_cost_per_call, "currency": pol.currency})
    return _serialize(pol)


# ---- Base de registros migrados (Governança IA — 30 dias), anonimizados ----
@router.get("/registry")
def registry_summary(db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    counts = {}
    for (r,) in db.query(RegistryRecord.registry).all():
        counts[r] = counts.get(r, 0) + 1
    return {"registries": counts, "total": sum(counts.values())}


@router.get("/registry/{name}")
def registry_list(name: str, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    rows = db.query(RegistryRecord).filter(RegistryRecord.registry == name).order_by(RegistryRecord.id).all()
    out = []
    for r in rows:
        try:
            rec = json.loads(r.data)
        except Exception:
            rec = {}
        out.append({"code": r.code, **rec})
    return out


# ---- Pessoas & skills ----
@router.get("/skills")
def list_skills(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return _list(db, SkillItem)


@router.post("/skills", status_code=201)
def create_skill(item: SkillItemIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
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
def create_initiative(item: InitiativeIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
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
def create_incident(item: IncidentIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    obj = Incident(**item.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "incident", obj.id, {"title": obj.title, "criticality": obj.criticality})
    return _serialize(obj)


# ---- Indicadores (KPIs dos painéis) — contabilizados da base migrada ----
def _reg(db: Session, name: str):
    out = []
    for r in db.query(RegistryRecord).filter(RegistryRecord.registry == name).all():
        try:
            out.append(json.loads(r.data))
        except Exception:
            pass
    return out


def _num(v, default=0):
    try:
        return float(v)
    except Exception:
        return default


@router.get("/overview")
def overview(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    from collections import Counter
    asset = _reg(db, "asset"); risk = _reg(db, "risk"); know = _reg(db, "knowledge")
    opp = _reg(db, "opportunity"); diag = _reg(db, "diagnostic")
    dmap = {(r.get("Indicador") or ""): r.get("Valor") for r in diag if r.get("Indicador")}
    dget = lambda k, d=0: dmap.get(k, d) if dmap.get(k) is not None else d

    total_col = int(_num(dget("Respondentes", len(asset)))) or len(asset)
    sens = int(_num(dget("Declaram uso de dados sensíveis/estratégicos em IA pública",
                         sum(1 for a in asset if a.get("Usa dado sensível") == "Sim"))))
    exposicao = int(_num(dget("Superfície de exposição potencial (sim + não sei)",
                         sum(1 for a in asset if a.get("Usa dado sensível") in ("Sim", "Não sei")))))
    gaps = int(_num(dget("Instâncias de uso sem licença correspondente (gap)", 0)))
    mencoes = int(_num(dget("Menções a ferramentas de IA (uso declarado)", 0)))
    media_fer = _num(dget("Média de ferramentas por colaborador", 0))
    coorte = int(_num(dget("Coorte crítica: dados sensíveis + sem licença", 0)))

    ativos_know = len(know)
    tipo_c = Counter((k.get("Tipo") or "—") for k in know)
    sev_c = Counter((r.get("Severidade") or "—") for r in risk)
    riscos_abertos = sum(1 for r in risk if (r.get("Status") or "Aberto") != "Fechado")
    col_com_gap = sum(1 for a in asset if (a.get("Gap (uso sem licença)") or "") not in ("", "Não", "—"))
    opp_p1 = sum(1 for o in opp if o.get("Prioridade") == "P1")

    area_c = Counter((a.get("Macroárea") or "—") for a in asset)
    know_area = Counter((k.get("Macroárea") or "—") for k in know)
    adocao = [{"area": a, "percent": round(100 * n / max(1, len(asset)))} for a, n in area_c.most_common(6)]
    prioridades = [{"nome": o.get("Cluster de dor") or o.get("OPP-ID") or "—",
                    "area": o.get("Macroárea mais afetada") or "",
                    "prioridade": o.get("Prioridade") or ""}
                   for o in sorted(opp, key=lambda o: (o.get("Prioridade") or "P9"))[:6]]
    sev_rank = {"Crítico": 0, "Alto": 1, "Médio": 2, "Baixo": 3}
    riscos = [{"code": r.get("RISK-ID") or "", "area": r.get("Macroárea") or "",
               "severidade": r.get("Severidade") or "", "status": r.get("Status") or ""}
              for r in sorted(risk, key=lambda r: sev_rank.get(r.get("Severidade"), 9))[:8]]
    tool_c = Counter()
    for a in asset:
        for t in str(a.get("Ferramentas em uso") or "").split(","):
            t = t.strip()
            if t:
                tool_c[t] += 1
    stack_top = [{"ferramenta": t, "usos": n} for t, n in tool_c.most_common(8)]
    capacidade = [{"area": a, "colaboradores": area_c.get(a, 0), "ativos": know_area.get(a, 0)}
                  for a, _ in area_c.most_common(6)]
    knowledge_tipos = [{"tipo": t, "qtd": n, "percent": round(100 * n / max(1, ativos_know))}
                       for t, n in tipo_c.most_common()]
    # Ranking de setores (macroáreas) centralizado nos ativos digitais (base de conhecimento).
    know_items: dict = {}
    for k in know:
        a = k.get("Macroárea") or "—"
        titulo = str(k.get("Tarefa que gostaria de delegar a um Agente Vanguarda")
                     or k.get("Ativo declarado (prompt/fluxo/automação)") or "").strip()
        know_items.setdefault(a, []).append({
            "code": k.get("KNOW-ID") or "",
            "tipo": k.get("Tipo") or "Prompt",
            "titulo": (titulo[:120] or "—"),
        })
    ranking_setores = [{"pos": i + 1, "setor": a, "ativos": n,
                        "percent": round(100 * n / max(1, ativos_know)),
                        "itens": know_items.get(a, [])}
                       for i, (a, n) in enumerate(know_area.most_common()) if a and a != "—"]

    pol = get_or_create_policy(db)
    prompts = db.query(PromptItem).all()
    acima = [p for p in prompts if (p.cost_per_call or 0) > pol.max_cost_per_call] if pol.max_cost_per_call else []
    since = datetime.now(timezone.utc) - timedelta(days=30)
    audits_month = db.query(AuditLog).filter(AuditLog.timestamp >= since).count()

    return {
        "custo": {
            "teto_por_chamada": pol.max_cost_per_call,
            "moeda": pol.currency,
            "prompts_acima_do_teto": len(acima),
            "prompts_avaliados": len(prompts),
        },
        "dashboard": {
            "colaboradores": total_col,
            "com_dado_sensivel": sens,
            "ativos_conhecimento": ativos_know,
            "prompts_conhecimento": tipo_c.get("Prompt", 0),
            "riscos_abertos": riscos_abertos,
            "riscos_criticos": sev_c.get("Crítico", 0),
            "riscos_altos": sev_c.get("Alto", 0),
            "gaps_licenca": gaps,
            "colaboradores_com_gap": col_com_gap,
            "oportunidades": len(opp),
            "oportunidades_p1": opp_p1,
            "media_ferramentas": round(media_fer, 2),
            "mencoes_ferramentas": mencoes,
        },
        "compliance": {
            "riscos_abertos": riscos_abertos,
            "alta_severidade": sev_c.get("Alto", 0),
            "criticos": sev_c.get("Crítico", 0),
            "exposicao": exposicao,
            "exposicao_pct": round(100 * exposicao / max(1, total_col)),
            "coorte_critica": coorte,
            "auditorias_mes": audits_month,
        },
        "adocao": adocao,
        "prioridades": prioridades,
        "riscos": riscos,
        "stack_top": stack_top,
        "capacidade": capacidade,
        "knowledge_tipos": knowledge_tipos,
        "ranking_setores": ranking_setores,
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
def seed_registros(db: Session):
    """Carrega os registros anonimizados (30 dias) do JSON versionado, se vazio."""
    if db.query(RegistryRecord).first():
        return
    path = os.path.join(os.path.dirname(__file__), "data", "registros_30dias.json")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for reg, recs in data.items():
        for rec in recs:
            code = ""
            for k, v in rec.items():
                if str(k).endswith("-ID") or k in ("Indicador", "#"):
                    code = "" if v is None else str(v)
                    break
            db.add(RegistryRecord(registry=reg, code=code, data=json.dumps(rec, ensure_ascii=False)))
    db.commit()


def seed_prompts_from_knowledge(db: Session):
    """Importa os ativos do Knowledge Registry para a Biblioteca como candidatos
    (status 'Revisão pendente') — a triar/homologar pelo administrador."""
    if db.query(PromptItem).filter(PromptItem.title.like("%[KNOW-%")).first():
        return
    seq: dict[str, int] = {}
    for r in db.query(RegistryRecord).filter(RegistryRecord.registry == "knowledge").order_by(RegistryRecord.id).all():
        try:
            rec = json.loads(r.data)
        except Exception:
            continue
        know_id = r.code or rec.get("KNOW-ID") or ""
        tipo = rec.get("Tipo") or "Prompt"
        area = rec.get("Macroárea") or ""
        tarefa = (rec.get("Tarefa que gostaria de delegar a um Agente Vanguarda")
                  or rec.get("Ativo declarado (prompt/fluxo/automação)") or "")
        desc = (str(tarefa).strip() or "Candidato do mapeamento — conteúdo a preencher na homologação.")[:380]
        title = (f"{tipo} · {area} [{know_id}]" if area else f"{tipo} [{know_id}]")[:200]
        # Metadados NIA-001: código de nomenclatura, tipo (A–E), autoria da origem.
        pref = _area_prefix(area or tipo)
        seq[pref] = seq.get(pref, 0) + 1
        db.add(PromptItem(
            title=title, description=desc, area=(area or tipo),
            control="Revisão pendente", content=str(tarefa),
            last_review="", uses=0, cost_per_call=0.0,
            code=f"PROMPT-{pref}-{seq[pref]:03d}",
            version="1.0", ptype=_ptype_from(f"{tipo} {area} {tarefa}"),
            tool="", author="Mapeamento de Governança", data_class="Uso interno",
        ))
    db.commit()


def seed_governance(db: Session):
    seed_registros(db)
    seed_prompts_from_knowledge(db)
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
    db.add(CostPolicy(max_cost_per_call=0.50, currency="BRL"))
    _curados = [
        dict(title="Briefing estratégico 360°", description="Transforma demanda em contexto, objetivos e critérios de entrega.",
             area="Planejamento", control="Aprovado", last_review="04 ago 2026", uses=86, cost_per_call=0.30,
             ptype="C", tool="ChatGPT Enterprise", author="Diretoria de IA", data_class="Uso interno"),
        dict(title="Legendas com voz de marca", description="Gera variações com tom, persona e restrições do cliente.",
             area="Social", control="Aprovado", last_review="02 ago 2026", uses=143, cost_per_call=0.18,
             ptype="E", tool="ChatGPT Enterprise", author="Diretoria de IA", data_class="Uso interno"),
        dict(title="Insight de performance semanal", description="Converte dados de mídia em decisões acionáveis.",
             area="Mídia", control="Revisão pendente", last_review="28 jul 2026", uses=48, cost_per_call=0.82,
             ptype="B", tool="Make / APIs", author="Diretoria de IA", data_class="Uso interno"),
    ]
    for c in _curados:
        c["code"] = _next_prompt_code(db, c["area"]); c["version"] = "1.0"
        db.add(PromptItem(**c)); db.flush()
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
    if not db.query(SupportTicket).first():
        db.add_all([
            SupportTicket(kind="Solicitação", subject="Homologação de nova ferramenta de vídeo",
                          area="Criação", severity="Média", status="Em atendimento",
                          message="Pedido de avaliação de ferramenta de geração de vídeo para a squad de criação.",
                          requester="Diretoria de IA", requester_email="admin@vanguardian.com"),
            SupportTicket(kind="Embaixadores", subject="Boa prática: prompt de brief que reduziu retrabalho",
                          area="Atendimento", severity="Baixa", status="Aberto",
                          message="Compartilhando um padrão de briefing que melhorou a taxa de aprovação. Sugiro incluir na Biblioteca.",
                          requester="Embaixador de IA", requester_email="user@vanguardamartech.com.br"),
            SupportTicket(kind="Uso indevido", subject="Uso de IA sem revisão humana em entrega a cliente",
                          area="Social", severity="Alta", status="Aberto",
                          message="Relato de conteúdo publicado sem a revisão obrigatória prevista na Política de IA.",
                          requester="Colaborador", requester_email="user@vanguardamartech.com.br"),
        ])
    db.commit()

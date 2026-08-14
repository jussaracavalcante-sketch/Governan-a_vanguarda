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


class Suggestion(Base):
    """Sugestões e melhorias: contribuições dos colaboradores e insumos do
    mapeamento de campo (ex.: tarefas que gostariam de delegar a um Agente)."""
    __tablename__ = "gov_suggestions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), default="")                 # ex.: KNOW-001 (origem mapeamento)
    title = Column(String(200), nullable=False)
    area = Column(String(120), default="")
    ptype = Column(String(1), default="")                 # A–E (herdado do mapeamento)
    message = Column(Text, default="")                    # texto da sugestão/melhoria
    source = Column(String(30), default="Colaborador")    # Colaborador | Mapeamento
    author = Column(String(120), default="")
    requester_email = Column(String(120), default="", index=True)
    status = Column(String(20), default="Nova")           # Nova | Em análise | Aceita | Recusada
    note = Column(Text, default="")
    handled_by = Column(String(120), default="")
    handled_at = Column(String(30), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Course(Base):
    """Base de Conhecimento — trilha/curso de capacitação (estilo Udemy) em
    IA, Compliance e Segurança da Informação. As aulas ficam em `lessons`
    (JSON: título, tipo, duração e link) e o progresso por aluno em
    CourseProgress."""
    __tablename__ = "gov_courses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), default="")                 # CURSO-NNN
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(40), default="IA")           # IA | Compliance | Segurança da Informação
    level = Column(String(20), default="Iniciante")       # Iniciante | Intermediário | Avançado
    instructor = Column(String(120), default="")
    cover = Column(String(8), default="🎓")                # emoji para a capa
    accent = Column(String(9), default="#6d28d9")         # cor de destaque da capa
    duration_min = Column(Integer, default=0)             # duração total (min)
    tags = Column(String(240), default="")                # csv
    lessons = Column(Text, default="[]")                  # JSON: [{title,type,duration_min,url}]
    published = Column(Boolean, default=True)
    # --- Gamificação / obrigatoriedade (estilo Hacker Rangers) ---
    mandatory = Column(Boolean, default=False)            # curso obrigatório
    due_date = Column(String(10), default="")             # prazo YYYY-MM-DD (obrigatórios)
    points = Column(Integer, default=50)                  # pontos ao concluir (ranking)
    pass_score = Column(Integer, default=70)              # nota mínima do quiz (%)
    quiz = Column(Text, default="[]")                     # JSON: [{q, options:[...], answer:idx}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CourseProgress(Base):
    """Progresso de um aluno em um curso (aulas + quiz + certificado)."""
    __tablename__ = "gov_course_progress"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, index=True, nullable=False)
    user_email = Column(String(120), default="", index=True)
    completed = Column(Text, default="[]")                # JSON: lista de índices de aulas concluídas
    status = Column(String(20), default="Em andamento")   # Em andamento | Concluído
    quiz_score = Column(Integer, default=-1)              # -1 = não realizado; 0..100
    quiz_passed = Column(Boolean, default=False)
    certificate_code = Column(String(40), default="")     # emitido ao concluir
    completed_at = Column(String(30), default="")
    updated_at = Column(String(30), default="")
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


class SuggestionIn(BaseModel):
    title: str
    area: str = ""
    message: str = ""


class SuggestionReviewIn(BaseModel):
    status: str | None = None           # Nova | Em análise | Aceita | Recusada
    note: str | None = None


class LessonIn(BaseModel):
    title: str
    type: str = "Vídeo"                  # Vídeo | Leitura | Quiz | Prática
    duration_min: int = 0
    url: str = ""


class QuestionIn(BaseModel):
    q: str
    options: list[str] = []
    answer: int = 0                      # índice da alternativa correta


class CourseIn(BaseModel):
    title: str
    description: str = ""
    category: str = "IA"                 # IA | Compliance | Segurança da Informação
    level: str = "Iniciante"
    instructor: str = ""
    cover: str = "🎓"
    accent: str = "#6d28d9"
    tags: str = ""
    published: bool = True
    mandatory: bool = False
    due_date: str = ""                   # YYYY-MM-DD
    points: int = 50
    pass_score: int = 70
    lessons: list[LessonIn] = []
    quiz: list[QuestionIn] = []


class CourseUpdateIn(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    level: str | None = None
    instructor: str | None = None
    cover: str | None = None
    accent: str | None = None
    tags: str | None = None
    published: bool | None = None
    mandatory: bool | None = None
    due_date: str | None = None
    points: int | None = None
    pass_score: int | None = None
    lessons: list[LessonIn] | None = None
    quiz: list[QuestionIn] | None = None


class ProgressIn(BaseModel):
    lesson_index: int
    done: bool = True


class QuizAnswerIn(BaseModel):
    answers: list[int] = []              # índice escolhido por questão


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


# ---- Sugestões e melhorias ----
@router.post("/suggestions", status_code=201)
def create_suggestion(item: SuggestionIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Qualquer colaborador envia uma sugestão ou melhoria."""
    forb = check_forbidden(item.title, item.message)
    if forb:
        raise HTTPException(status_code=422, detail={"regras": ["R1: conteúdo proibido — " + ", ".join(sorted(set(forb)))]})
    obj = Suggestion(
        title=item.title.strip()[:200], area=item.area.strip()[:120], message=item.message.strip(),
        source="Colaborador", author=(u.name or u.email), requester_email=u.email, status="Nova",
    )
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "suggestion", obj.id, {"title": obj.title})
    return _serialize(obj)


@router.get("/suggestions")
def list_suggestions(status: str = "", source: str = "", db: Session = Depends(get_db),
                     u: User = Depends(get_current_manager_user)):
    q = db.query(Suggestion)
    if status:
        q = q.filter(Suggestion.status == status)
    if source:
        q = q.filter(Suggestion.source == source)
    return [_serialize(o) for o in q.order_by(Suggestion.id.desc()).all()]


@router.get("/suggestions/mine")
def my_suggestions(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    rows = (db.query(Suggestion).filter(Suggestion.requester_email == u.email)
            .order_by(Suggestion.id.desc()).all())
    return [_serialize(o) for o in rows]


@router.put("/suggestions/{sid}")
def review_suggestion(sid: int, item: SuggestionReviewIn, db: Session = Depends(get_db),
                      u: User = Depends(get_current_manager_user)):
    obj = db.query(Suggestion).filter(Suggestion.id == sid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")
    if item.status is not None:
        obj.status = item.status
    if item.note is not None:
        obj.note = item.note
    obj.handled_by = u.name or u.email
    obj.handled_at = _hoje_pt()
    db.commit(); db.refresh(obj)
    _audit(db, u, "UPDATE", "suggestion", obj.id, {"status": obj.status})
    return _serialize(obj)


# ---- Base de Conhecimento (cursos e trilhas de capacitação) ----
COURSE_CATEGORIES = ("IA", "Compliance", "Segurança da Informação")
COURSE_LEVELS = ("Iniciante", "Intermediário", "Avançado")


def _next_course_code(db: Session) -> str:
    n = db.query(Course).count() + 1
    while db.query(Course).filter(Course.code == f"CURSO-{n:03d}").first():
        n += 1
    return f"CURSO-{n:03d}"


def _json_list(txt: str) -> list:
    try:
        data = json.loads(txt or "[]")
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _lessons_list(obj: Course) -> list:
    return _json_list(obj.lessons)


def _quiz_list(obj: Course) -> list:
    return _json_list(obj.quiz)


def _parse_date(s: str):
    try:
        return datetime.strptime((s or "").strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def _recompute_progress(obj: Course, prog: "CourseProgress") -> None:
    """Recalcula status, conclusão e emissão de certificado (mutates prog)."""
    total = len(_lessons_list(obj))
    has_quiz = len(_quiz_list(obj)) > 0
    try:
        done = sorted(set(i for i in json.loads(prog.completed or "[]") if isinstance(i, int) and 0 <= i < total))
    except Exception:
        done = []
    lessons_done = len(done) >= total
    quiz_ok = (not has_quiz) or bool(prog.quiz_passed)
    completed = lessons_done and quiz_ok and (total > 0 or has_quiz)
    prog.status = "Concluído" if completed else "Em andamento"
    if completed and not prog.certificate_code:
        prog.certificate_code = f"CERT-{obj.id:03d}-{prog.id:05d}"
        prog.completed_at = _hoje_pt()


def _course_public(obj: Course, prog: "CourseProgress | None") -> dict:
    lessons = _lessons_list(obj)
    total = len(lessons)
    quiz = _quiz_list(obj)
    has_quiz = len(quiz) > 0
    done = []
    if prog:
        try:
            done = sorted(set(i for i in json.loads(prog.completed or "[]") if isinstance(i, int) and 0 <= i < total))
        except Exception:
            done = []
    steps_total = total + (1 if has_quiz else 0)
    steps_done = len(done) + (1 if (has_quiz and prog and prog.quiz_passed) else 0)
    pct = round(100 * steps_done / steps_total) if steps_total else 0
    status = "Não iniciado"
    if prog:
        status = prog.status or "Em andamento"
    # prazo (obrigatórios)
    due = _parse_date(obj.due_date)
    days_left = None; overdue = False
    if due:
        days_left = (due - datetime.now().date()).days
        overdue = (days_left < 0) and (status != "Concluído")
    # quiz sem gabarito (não expõe a resposta correta)
    quiz_public = [{"q": q.get("q", ""), "options": q.get("options", [])} for q in quiz]
    return {
        "id": obj.id, "code": obj.code, "title": obj.title, "description": obj.description,
        "category": obj.category, "level": obj.level, "instructor": obj.instructor,
        "cover": obj.cover, "accent": obj.accent, "tags": obj.tags,
        "duration_min": obj.duration_min, "published": obj.published,
        "mandatory": bool(obj.mandatory), "due_date": obj.due_date or "",
        "days_left": days_left, "overdue": overdue,
        "points": obj.points or 0, "pass_score": obj.pass_score or 0,
        "lessons": lessons, "lessons_count": total,
        "quiz": quiz_public, "quiz_count": len(quiz), "has_quiz": has_quiz,
        "my_completed": done, "my_percent": pct, "my_status": status,
        "my_quiz_score": (prog.quiz_score if prog else -1),
        "my_quiz_passed": bool(prog.quiz_passed) if prog else False,
        "my_certificate": (prog.certificate_code if prog else "") or "",
        "my_completed_at": (prog.completed_at if prog else "") or "",
    }


def _progress_for(db: Session, email: str, course_ids: list[int]) -> dict:
    if not course_ids:
        return {}
    rows = (db.query(CourseProgress)
            .filter(CourseProgress.user_email == email, CourseProgress.course_id.in_(course_ids)).all())
    return {r.course_id: r for r in rows}


@router.get("/courses")
def list_courses(category: str = "", level: str = "", q: str = "",
                 db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Catálogo da Base de Conhecimento. Colaboradores veem cursos publicados;
    gestores veem também rascunhos (não publicados)."""
    query = db.query(Course)
    if u.role not in ("Admin", "Manager"):
        query = query.filter(Course.published == True)  # noqa: E712
    if category:
        query = query.filter(Course.category == category)
    if level:
        query = query.filter(Course.level == level)
    rows = query.order_by(Course.id).all()
    if q:
        ql = q.lower()
        rows = [c for c in rows if ql in (c.title or "").lower()
                or ql in (c.description or "").lower() or ql in (c.tags or "").lower()]
    progs = _progress_for(db, u.email, [c.id for c in rows])
    return [_course_public(c, progs.get(c.id)) for c in rows]


@router.get("/courses/mine")
def my_learning(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Cursos em que o aluno tem progresso registrado (meus aprendizados)."""
    rows = (db.query(CourseProgress).filter(CourseProgress.user_email == u.email)
            .order_by(CourseProgress.updated_at.desc()).all())
    out = []
    for p in rows:
        c = db.query(Course).filter(Course.id == p.course_id).first()
        if c:
            out.append(_course_public(c, p))
    return out


@router.get("/courses/{cid}")
def get_course(cid: int, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    obj = db.query(Course).filter(Course.id == cid).first()
    if not obj or (not obj.published and u.role not in ("Admin", "Manager")):
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    prog = db.query(CourseProgress).filter(
        CourseProgress.user_email == u.email, CourseProgress.course_id == cid).first()
    return _course_public(obj, prog)


def _apply_course(obj: Course, lessons: list) -> None:
    clean = []
    for ls in lessons:
        d = ls.model_dump() if hasattr(ls, "model_dump") else dict(ls)
        clean.append({
            "title": str(d.get("title", "")).strip()[:200],
            "type": (d.get("type") or "Vídeo"),
            "duration_min": max(0, int(d.get("duration_min") or 0)),
            "url": str(d.get("url", "")).strip()[:400],
        })
    obj.lessons = json.dumps(clean, ensure_ascii=False)
    obj.duration_min = sum(l["duration_min"] for l in clean)


def _apply_quiz(obj: Course, quiz: list) -> None:
    clean = []
    for qq in quiz:
        d = qq.model_dump() if hasattr(qq, "model_dump") else dict(qq)
        opts = [str(o).strip()[:200] for o in (d.get("options") or []) if str(o).strip()]
        if not str(d.get("q", "")).strip() or len(opts) < 2:
            continue
        ans = int(d.get("answer") or 0)
        ans = ans if 0 <= ans < len(opts) else 0
        clean.append({"q": str(d.get("q")).strip()[:300], "options": opts, "answer": ans})
    obj.quiz = json.dumps(clean, ensure_ascii=False)


def _valid_due(s: str) -> str:
    s = (s or "").strip()
    return s if (s == "" or _parse_date(s)) else ""


@router.post("/courses", status_code=201)
def create_course(item: CourseIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    if item.category not in COURSE_CATEGORIES:
        raise HTTPException(status_code=422, detail={"regras": [f"Categoria inválida (use: {', '.join(COURSE_CATEGORIES)})"]})
    forb = check_forbidden(item.title, item.description)
    if forb:
        raise HTTPException(status_code=422, detail={"regras": ["R1: conteúdo proibido — " + ", ".join(sorted(set(forb)))]})
    obj = Course(
        code=_next_course_code(db), title=item.title.strip()[:200], description=item.description.strip(),
        category=item.category, level=(item.level if item.level in COURSE_LEVELS else "Iniciante"),
        instructor=(item.instructor.strip() or (u.name or u.email))[:120],
        cover=(item.cover or "🎓")[:8], accent=(item.accent or "#6d28d9")[:9],
        tags=item.tags.strip()[:240], published=bool(item.published),
        mandatory=bool(item.mandatory), due_date=_valid_due(item.due_date),
        points=max(0, int(item.points or 0)), pass_score=min(100, max(0, int(item.pass_score or 70))),
    )
    _apply_course(obj, item.lessons)
    _apply_quiz(obj, item.quiz)
    db.add(obj); db.commit(); db.refresh(obj)
    _audit(db, u, "CREATE", "course", obj.id, {"title": obj.title, "category": obj.category, "mandatory": obj.mandatory})
    return _course_public(obj, None)


@router.put("/courses/{cid}")
def update_course(cid: int, item: CourseUpdateIn, db: Session = Depends(get_db), u: User = Depends(get_current_manager_user)):
    obj = db.query(Course).filter(Course.id == cid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    data = item.model_dump(exclude_unset=True)
    if "category" in data and data["category"] not in COURSE_CATEGORIES:
        raise HTTPException(status_code=422, detail={"regras": [f"Categoria inválida (use: {', '.join(COURSE_CATEGORIES)})"]})
    if "level" in data and data["level"] not in COURSE_LEVELS:
        data.pop("level")
    forb = check_forbidden(data.get("title", ""), data.get("description", ""))
    if forb:
        raise HTTPException(status_code=422, detail={"regras": ["R1: conteúdo proibido — " + ", ".join(sorted(set(forb)))]})
    lessons = data.pop("lessons", None)
    quiz = data.pop("quiz", None)
    if "due_date" in data:
        data["due_date"] = _valid_due(data["due_date"])
    if "pass_score" in data and data["pass_score"] is not None:
        data["pass_score"] = min(100, max(0, int(data["pass_score"])))
    for k, v in data.items():
        setattr(obj, k, v)
    if lessons is not None:
        _apply_course(obj, item.lessons)
    if quiz is not None:
        _apply_quiz(obj, item.quiz)
    db.commit(); db.refresh(obj)
    _audit(db, u, "UPDATE", "course", obj.id, {"title": obj.title})
    return _course_public(obj, None)


def _get_or_create_prog(db: Session, cid: int, email: str) -> CourseProgress:
    prog = db.query(CourseProgress).filter(
        CourseProgress.user_email == email, CourseProgress.course_id == cid).first()
    if not prog:
        prog = CourseProgress(course_id=cid, user_email=email, completed="[]", quiz_score=-1)
        db.add(prog); db.flush()
    return prog


@router.post("/courses/{cid}/progress")
def set_progress(cid: int, item: ProgressIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Marca/desmarca uma aula como concluída para o aluno atual."""
    obj = db.query(Course).filter(Course.id == cid).first()
    if not obj or (not obj.published and u.role not in ("Admin", "Manager")):
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    total = len(_lessons_list(obj))
    if not (0 <= item.lesson_index < total):
        raise HTTPException(status_code=422, detail="Índice de aula inválido")
    prog = _get_or_create_prog(db, cid, u.email)
    was_done = bool(prog.certificate_code)
    try:
        done = set(i for i in json.loads(prog.completed or "[]") if isinstance(i, int))
    except Exception:
        done = set()
    if item.done:
        done.add(item.lesson_index)
    else:
        done.discard(item.lesson_index)
    done = sorted(i for i in done if 0 <= i < total)
    prog.completed = json.dumps(done, ensure_ascii=False)
    prog.updated_at = _hoje_pt()
    _recompute_progress(obj, prog)
    db.commit(); db.refresh(prog)
    if prog.status == "Concluído" and not was_done:
        _audit(db, u, "COMPLETE", "course", cid, {"course": obj.title, "certificate": prog.certificate_code})
    return _course_public(obj, prog)


@router.post("/courses/{cid}/quiz")
def submit_quiz(cid: int, item: QuizAnswerIn, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Corrige o quiz, guarda a nota e (se aprovado + aulas concluídas) emite certificado."""
    obj = db.query(Course).filter(Course.id == cid).first()
    if not obj or (not obj.published and u.role not in ("Admin", "Manager")):
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    quiz = _quiz_list(obj)
    if not quiz:
        raise HTTPException(status_code=422, detail="Este curso não possui quiz")
    answers = list(item.answers or [])
    correct = sum(1 for i, q in enumerate(quiz)
                  if i < len(answers) and answers[i] == int(q.get("answer", -1)))
    score = round(100 * correct / len(quiz))
    passed = score >= (obj.pass_score or 70)
    prog = _get_or_create_prog(db, cid, u.email)
    was_done = bool(prog.certificate_code)
    prog.quiz_score = score
    prog.quiz_passed = passed
    prog.updated_at = _hoje_pt()
    _recompute_progress(obj, prog)
    db.commit(); db.refresh(prog)
    _audit(db, u, "QUIZ", "course", cid, {"course": obj.title, "score": score, "passed": passed})
    if prog.status == "Concluído" and not was_done:
        _audit(db, u, "COMPLETE", "course", cid, {"course": obj.title, "certificate": prog.certificate_code})
    return {"score": score, "passed": passed, "correct": correct, "total": len(quiz),
            "pass_score": obj.pass_score or 70, "course": _course_public(obj, prog)}


@router.get("/courses/{cid}/certificate")
def get_certificate(cid: int, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Dados do certificado do aluno para o curso (se concluído)."""
    obj = db.query(Course).filter(Course.id == cid).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    prog = db.query(CourseProgress).filter(
        CourseProgress.user_email == u.email, CourseProgress.course_id == cid).first()
    if not prog or not prog.certificate_code:
        raise HTTPException(status_code=404, detail="Certificado ainda não emitido — conclua o curso.")
    return {
        "code": prog.certificate_code, "student": (u.name or u.email), "email": u.email,
        "course": obj.title, "course_code": obj.code, "category": obj.category,
        "level": obj.level, "instructor": obj.instructor or "Vanguarda Martech",
        "duration_min": obj.duration_min, "issued_at": prog.completed_at or _hoje_pt(),
        "quiz_score": prog.quiz_score if prog.quiz_score is not None else -1,
    }


@router.get("/courses-ranking")
def courses_ranking(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    """Ranking de aprendizado (estilo Hacker Rangers): pontos por cursos concluídos."""
    points = {c.id: (c.points or 0) for c in db.query(Course).all()}
    titles = {c.id: c.title for c in db.query(Course).all()}
    agg = {}
    for p in db.query(CourseProgress).filter(CourseProgress.status == "Concluído").all():
        e = p.user_email or "—"
        d = agg.setdefault(e, {"email": e, "points": 0, "courses": 0})
        d["points"] += points.get(p.course_id, 0)
        d["courses"] += 1
    # nomes
    names = {usr.email: usr.name for usr in db.query(User).all()}
    rows = []
    for e, d in agg.items():
        rows.append({"email": e, "name": names.get(e, e.split("@")[0]),
                     "points": d["points"], "courses": d["courses"],
                     "me": (e == u.email)})
    rows.sort(key=lambda r: (-r["points"], -r["courses"], r["name"].lower()))
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


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


def seed_suggestions_from_knowledge(db: Session):
    """Importa os insumos do mapeamento (Knowledge Registry) para o canal de
    'Sugestões e melhorias' — a Biblioteca fica só com prompts curados/reais."""
    if db.query(Suggestion).filter(Suggestion.source == "Mapeamento").first():
        return
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
        title = (f"{tipo} · {area} [{know_id}]" if area else f"{tipo} [{know_id}]")[:200]
        db.add(Suggestion(
            code=str(know_id), title=title, area=(area or tipo),
            ptype=_ptype_from(f"{tipo} {area} {tarefa}"),
            message=str(tarefa).strip() or "(sem descrição no mapeamento)",
            source="Mapeamento", author="Mapeamento de Governança",
            requester_email="", status="Nova",
        ))
    db.commit()


def seed_courses(db: Session):
    """Cursos iniciais da Base de Conhecimento (IA, Compliance e Segurança da Informação)."""
    if db.query(Course).first():
        return
    due30 = (datetime.now().date() + timedelta(days=30)).isoformat()
    due45 = (datetime.now().date() + timedelta(days=45)).isoformat()
    catalogo = [
        dict(title="Fundamentos de IA Generativa no trabalho", category="IA", level="Iniciante",
             instructor="Diretoria de IA", cover="🤖", accent="#6d28d9", points=50, pass_score=70,
             description="O que é IA generativa, onde ela ajuda no dia a dia da Vanguarda e como usar com responsabilidade.",
             tags="ia,generativa,fundamentos,produtividade",
             lessons=[
                 dict(title="Boas-vindas e panorama da IA na Vanguarda", type="Vídeo", duration_min=8),
                 dict(title="Como os modelos de linguagem funcionam (sem jargão)", type="Vídeo", duration_min=14),
                 dict(title="Casos de uso por área", type="Leitura", duration_min=10),
                 dict(title="Limites e riscos (alucinação, viés)", type="Vídeo", duration_min=12),
             ],
             quiz=[
                 dict(q="IA generativa pode 'alucinar' (inventar informações)?", options=["Nunca, é sempre precisa", "Sim, por isso exige revisão humana", "Só em inglês"], answer=1),
                 dict(q="Onde a IA mais ajuda no dia a dia?", options=["Substituir a revisão humana", "Acelerar rascunhos e análises com supervisão", "Guardar senhas"], answer=1),
                 dict(q="Antes de entregar conteúdo gerado por IA ao cliente, você deve:", options=["Publicar direto", "Revisar e validar", "Ignorar a política"], answer=1),
             ]),
        dict(title="Engenharia de Prompts (padrão NIA-001)", category="IA", level="Intermediário",
             instructor="Diretoria de IA", cover="✍️", accent="#2563eb", points=70, pass_score=70,
             description="Escreva prompts consistentes e versionáveis seguindo o padrão corporativo NIA-001.",
             tags="prompt,nia-001,versionamento,qualidade",
             lessons=[
                 dict(title="Anatomia de um bom prompt", type="Vídeo", duration_min=11),
                 dict(title="Padrão NIA-001: código, versão e classificação", type="Leitura", duration_min=15),
                 dict(title="Contexto, restrições e critérios de saída", type="Vídeo", duration_min=13),
                 dict(title="Prática: transformando um brief em prompt", type="Prática", duration_min=20),
             ]),
        dict(title="Política de IA e uso responsável", category="Compliance", level="Iniciante",
             instructor="Compliance & Governança", cover="⚖️", accent="#059669",
             mandatory=True, due_date=due30, points=100, pass_score=80,
             description="Regras da Política de IA da Vanguarda: revisão humana, ferramentas homologadas e classificação da informação. Treinamento obrigatório.",
             tags="politica,compliance,uso-responsavel,governanca,obrigatório",
             lessons=[
                 dict(title="Princípios da Política de IA", type="Leitura", duration_min=12),
                 dict(title="Revisão humana obrigatória", type="Vídeo", duration_min=9),
                 dict(title="Ferramentas homologadas x não homologadas", type="Vídeo", duration_min=10),
                 dict(title="Fluxo de reporte de uso indevido", type="Leitura", duration_min=7),
             ],
             quiz=[
                 dict(q="Entregas externas feitas com IA exigem:", options=["Nada", "Revisão humana responsável", "Aprovação do cliente apenas"], answer=1),
                 dict(q="Posso usar qualquer ferramenta de IA que eu quiser?", options=["Sim", "Só as homologadas no stack", "Só as gratuitas"], answer=1),
                 dict(q="Dado classificado como Restrito pode ir para repositório público externo?", options=["Sim", "Não", "Se for pequeno"], answer=1),
                 dict(q="Ao presenciar uso indevido de IA, devo:", options=["Ignorar", "Reportar pelo canal de suporte", "Comentar informalmente"], answer=1),
             ]),
        dict(title="LGPD na prática para agências", category="Compliance", level="Intermediário",
             instructor="Compliance & Governança", cover="🛡️", accent="#0d9488", points=80, pass_score=75,
             description="Bases legais, dados pessoais de clientes e cuidados ao usar IA com informação sensível.",
             tags="lgpd,dados-pessoais,privacidade,clientes",
             lessons=[
                 dict(title="Conceitos: dado pessoal e dado sensível", type="Vídeo", duration_min=12),
                 dict(title="Bases legais e consentimento", type="Leitura", duration_min=14),
                 dict(title="IA + dados de cliente: o que pode e o que não pode", type="Vídeo", duration_min=13),
                 dict(title="Incidentes e notificação", type="Leitura", duration_min=9),
             ],
             quiz=[
                 dict(q="Dado sensível inclui:", options=["Nome comercial da empresa", "Origem racial, saúde, biometria", "CNPJ público"], answer=1),
                 dict(q="Posso colar dados pessoais de cliente numa IA não homologada?", options=["Sim", "Não", "Se anonimizar o nome só"], answer=1),
                 dict(q="Em caso de incidente com dados pessoais, o correto é:", options=["Esconder", "Notificar conforme o fluxo", "Apagar tudo"], answer=1),
             ]),
        dict(title="Segurança da Informação: o essencial", category="Segurança da Informação", level="Iniciante",
             instructor="Segurança da Informação", cover="🔐", accent="#dc2626",
             mandatory=True, due_date=due45, points=100, pass_score=80,
             description="Higiene digital para o time: senhas, MFA, phishing e classificação de dados. Treinamento obrigatório.",
             tags="seguranca,senhas,mfa,phishing,obrigatório",
             lessons=[
                 dict(title="Senhas fortes e gerenciadores", type="Vídeo", duration_min=8),
                 dict(title="MFA: por que e como ativar", type="Vídeo", duration_min=7),
                 dict(title="Reconhecendo phishing e engenharia social", type="Vídeo", duration_min=12),
                 dict(title="Classificação da informação (público/interno/restrito)", type="Leitura", duration_min=10),
             ],
             quiz=[
                 dict(q="Uma senha forte deve ser:", options=["Curta e fácil", "Longa, única e guardada em gerenciador", "A mesma em todos os sites"], answer=1),
                 dict(q="MFA serve para:", options=["Deixar o login mais lento", "Adicionar uma 2ª camada de proteção", "Trocar a senha"], answer=1),
                 dict(q="Recebeu um e-mail urgente pedindo sua senha. Você:", options=["Responde com a senha", "Desconfia — é provável phishing", "Encaminha para todos"], answer=1),
                 dict(q="Um contrato de cliente deve ser classificado como:", options=["Público", "Restrito/Confidencial", "Não precisa classificar"], answer=1),
             ]),
        dict(title="Uso seguro de IA e proteção de segredos", category="Segurança da Informação", level="Avançado",
             instructor="Segurança da Informação", cover="🕵️", accent="#b91c1c", points=90, pass_score=80,
             description="Como evitar vazamento de dados e segredos ao usar ferramentas de IA e integrações.",
             tags="seguranca,ia,segredos,vazamento,api",
             lessons=[
                 dict(title="O que nunca colar em uma IA", type="Vídeo", duration_min=10),
                 dict(title="Chaves, tokens e credenciais", type="Leitura", duration_min=12),
                 dict(title="Ambientes homologados e retenção de dados", type="Vídeo", duration_min=13),
                 dict(title="Prática: revisando um prompt de risco", type="Prática", duration_min=18),
             ],
             quiz=[
                 dict(q="O que NÃO se deve colar numa IA pública?", options=["Um texto de blog", "Chaves de API e dados de cliente", "Uma pergunta genérica"], answer=1),
                 dict(q="Tokens e senhas devem ficar:", options=["No prompt", "Em cofre/secret manager", "Num post-it"], answer=1),
             ]),
    ]
    for c in catalogo:
        lessons = c.pop("lessons"); quiz = c.pop("quiz", [])
        obj = Course(code=_next_course_code(db), published=True, **c)
        obj.lessons = json.dumps(lessons, ensure_ascii=False)
        obj.quiz = json.dumps(quiz, ensure_ascii=False)
        obj.duration_min = sum(int(l.get("duration_min") or 0) for l in lessons)
        db.add(obj); db.flush()
    db.commit()


def seed_governance(db: Session):
    seed_registros(db)
    seed_suggestions_from_knowledge(db)
    seed_courses(db)
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

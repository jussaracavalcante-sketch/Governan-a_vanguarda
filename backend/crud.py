"""
VANGUARDIAN - CRUD Operations
Database operations for all models.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from models import (
    User, Tool, Skill, Prompt, Activity,
    AuditLog, IntegrationConfig, IntegrationSyncLog
)
from schemas import (
    UserCreate, UserUpdate,
    ToolCreate, ToolUpdate,
    SkillCreate, SkillUpdate,
    PromptCreate, PromptUpdate,
    ActivityCreate,
    DashboardStats,
    IntegrationConfigCreate, IntegrationConfigUpdate,
    IntegrationSyncLogCreate,
)
from auth.security import get_password_hash
import json
from datetime import date


# ─── USER ───
def create_user(db: Session, obj: dict) -> User:
    db_obj = User(**obj)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, search: str = ""):
    q = db.query(User)
    if search:
        q = q.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    return q.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, obj: dict) -> User | None:
    db_obj = get_user(db, user_id)
    if not db_obj:
        return None
    for field, value in obj.items():
        if hasattr(db_obj, field):
            setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_user(db: Session, user_id: int) -> User | None:
    db_obj = get_user(db, user_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# ─── TOOL ───
def create_tool(db: Session, obj: ToolCreate) -> Tool:
    db_obj = Tool(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_tools(db: Session, skip: int = 0, limit: int = 100, search: str = ""):
    q = db.query(Tool)
    if search:
        q = q.filter(
            or_(
                Tool.name.ilike(f"%{search}%"),
                Tool.team.ilike(f"%{search}%")
            )
        )
    return q.offset(skip).limit(limit).all()


def get_tool(db: Session, tool_id: int) -> Tool | None:
    return db.query(Tool).filter(Tool.id == tool_id).first()


def update_tool(db: Session, tool_id: int, obj: ToolUpdate) -> Tool | None:
    db_obj = get_tool(db, tool_id)
    if not db_obj:
        return None
    for field, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_tool(db: Session, tool_id: int) -> Tool | None:
    db_obj = get_tool(db, tool_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# ─── SKILL ───
def create_skill(db: Session, obj: SkillCreate) -> Skill:
    db_obj = Skill(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_skills(db: Session, skip: int = 0, limit: int = 100, search: str = ""):
    q = db.query(Skill)
    if search:
        q = q.filter(
            or_(
                Skill.skill.ilike(f"%{search}%"),
                Skill.team.ilike(f"%{search}%")
            )
        )
    return q.offset(skip).limit(limit).all()


def get_skill(db: Session, skill_id: int) -> Skill | None:
    return db.query(Skill).filter(Skill.id == skill_id).first()


def update_skill(db: Session, skill_id: int, obj: SkillUpdate) -> Skill | None:
    db_obj = get_skill(db, skill_id)
    if not db_obj:
        return None
    for field, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_skill(db: Session, skill_id: int) -> Skill | None:
    db_obj = get_skill(db, skill_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# ─── PROMPT ───
def create_prompt(db: Session, obj: PromptCreate) -> Prompt:
    db_obj = Prompt(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_prompts(db: Session, skip: int = 0, limit: int = 100, search: str = "", category: str = ""):
    q = db.query(Prompt)
    if search:
        q = q.filter(
            or_(
                Prompt.title.ilike(f"%{search}%"),
                Prompt.text.ilike(f"%{search}%")
            )
        )
    if category:
        q = q.filter(Prompt.category == category)
    return q.offset(skip).limit(limit).all()


def get_prompt(db: Session, prompt_id: int) -> Prompt | None:
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()


def update_prompt(db: Session, prompt_id: int, obj: PromptUpdate) -> Prompt | None:
    db_obj = get_prompt(db, prompt_id)
    if not db_obj:
        return None
    for field, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_prompt(db: Session, prompt_id: int) -> Prompt | None:
    db_obj = get_prompt(db, prompt_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# ─── ACTIVITY ───
def create_activity(db: Session, obj: ActivityCreate) -> Activity:
    db_obj = Activity(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_activities(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Activity).order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()


# ─── AUDIT LOG ───
def create_audit_log(db: Session, obj: dict) -> AuditLog:
    db_obj = AuditLog(**obj)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if start_date:
        q = q.filter(AuditLog.timestamp >= start_date)
    if end_date:
        q = q.filter(AuditLog.timestamp <= end_date)
    return q.offset(skip).limit(limit).all()


# ─── INTEGRATION CONFIG ───
def create_integration_config(db: Session, obj: IntegrationConfigCreate) -> IntegrationConfig:
    db_obj = IntegrationConfig(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_integration_configs(db: Session):
    return db.query(IntegrationConfig).all()


def get_integration_config(db: Session, config_id: int) -> IntegrationConfig | None:
    return db.query(IntegrationConfig).filter(IntegrationConfig.id == config_id).first()


def get_integration_config_by_name(db: Session, name: str) -> IntegrationConfig | None:
    return db.query(IntegrationConfig).filter(IntegrationConfig.name == name).first()


def update_integration_config(db: Session, config_id: int, obj: IntegrationConfigUpdate) -> IntegrationConfig | None:
    db_obj = get_integration_config(db, config_id)
    if not db_obj:
        return None
    for field, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_integration_config(db: Session, config_id: int) -> IntegrationConfig | None:
    db_obj = get_integration_config(db, config_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# ─── INTEGRATION SYNC LOG ───
def create_sync_log(db: Session, obj: IntegrationSyncLogCreate) -> IntegrationSyncLog:
    db_obj = IntegrationSyncLog(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_sync_logs(db: Session, integration_id: int | None = None, skip: int = 0, limit: int = 50):
    q = db.query(IntegrationSyncLog).order_by(IntegrationSyncLog.started_at.desc())
    if integration_id:
        q = q.filter(IntegrationSyncLog.integration_id == integration_id)
    return q.offset(skip).limit(limit).all()


def update_sync_log(db: Session, log_id: int, obj: dict) -> IntegrationSyncLog | None:
    db_obj = db.query(IntegrationSyncLog).filter(IntegrationSyncLog.id == log_id).first()
    if not db_obj:
        return None
    for field, value in obj.items():
        if hasattr(db_obj, field):
            setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# ─── DASHBOARD ───
def get_dashboard_stats(db: Session) -> DashboardStats:
    total_users = db.query(User).count()
    from models import UserStatus, ToolStatus, SkillLevel
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    total_tools = db.query(Tool).count()
    active_tools = db.query(Tool).filter(Tool.status == ToolStatus.ACTIVE).count()
    total_skills = db.query(Skill).count()
    total_prompts = db.query(Prompt).count()
    favorite_prompts = db.query(Prompt).filter(Prompt.is_favorite == True).count()
    total_teams = db.query(Skill.team).distinct().count()
    critical_skills = db.query(Skill).filter(Skill.level == SkillLevel.BEGINNER).count()

    levels = {"Iniciante": 25, "Intermediário": 50, "Avançado": 75, "Especialista": 100}
    skills = db.query(Skill.level).all()
    avg_skill_level = (
        sum(levels.get(s[0], 0) for s in skills) / len(skills) if skills else 0
    )

    recent_activities = get_activities(db, limit=5)

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_tools=total_tools,
        active_tools=active_tools,
        total_skills=total_skills,
        total_prompts=total_prompts,
        favorite_prompts=favorite_prompts,
        total_teams=total_teams,
        avg_skill_level=round(avg_skill_level, 1),
        critical_skills=critical_skills,
        recent_activities=recent_activities,
    )


# ─── SEED ───
def seed_initial_data(db: Session):
    """Seed database with initial data if empty."""
    # Check if users exist
    if db.query(User).first():
        return

    # Create admin user
    admin = User(
        name="Administrador",
        email="admin@vanguardian.local",
        hashed_password=get_password_hash("admin123"),
        role="Admin",
        status="Ativo",
        is_superuser=True,
        last_access=date.today().isoformat(),
    )
    db.add(admin)

    # Create sample users
    users = [
        User(name="Ana Souza", email="ana.souza@empresa.com", hashed_password=get_password_hash("123456"), role="Manager", status="Ativo"),
        User(name="Bruno Lima", email="bruno.lima@empresa.com", hashed_password=get_password_hash("123456"), role="User", status="Ativo"),
        User(name="Carla Mendes", email="carla.m@empresa.com", hashed_password=get_password_hash("123456"), role="User", status="Inativo"),
    ]
    db.add_all(users)

    # Create sample tools
    tools = [
        Tool(name="Jira", category="Gestão", team="Engenharia", status="Ativa", acquisition_date="2023-03-10"),
        Tool(name="Figma", category="Design", team="Produto", status="Ativa", acquisition_date="2022-11-05"),
        Tool(name="Slack", category="Comunicação", team="Geral", status="Ativa", acquisition_date="2021-01-15"),
        Tool(name="Salesforce", category="CRM", team="Vendas", status="Manutenção", acquisition_date="2020-08-20"),
    ]
    db.add_all(tools)

    # Create sample skills
    skills = [
        Skill(team="Engenharia", skill="React", category="Frontend", level="Avançado", reviewer="Ana Souza", updated_date="2026-07-10"),
        Skill(team="Engenharia", skill="Node.js", category="Backend", level="Avançado", reviewer="Bruno Lima", updated_date="2026-07-12"),
        Skill(team="Produto", skill="UX Research", category="Design", level="Intermediário", reviewer="Carla Mendes", updated_date="2026-06-28"),
        Skill(team="Dados", skill="Machine Learning", category="Data Science", level="Iniciante", reviewer="Ana Souza", updated_date="2026-05-15"),
    ]
    db.add_all(skills)

    # Create sample prompts
    prompts = [
        Prompt(title="Análise de Requisitos", category="Produto", text="Você é um Product Owner experiente. Analise os requisitos abaixo e identifique: (1) Dores do usuário, (2) Critérios de aceitação claros, (3) Dependências técnicas, (4) Riscos de negócio.\n\nRequisitos: {{ REQUISITOS }}", uses=42, is_favorite=True),
        Prompt(title="Code Review Profissional", category="Engenharia", text="Você é um Tech Lead sênior. Faça um code review da snippet abaixo focando em: legibilidade, segurança, performance, testabilidade e padrões de projeto.\n\nCódigo: {{ CODIGO }}", uses=35, is_favorite=True),
        Prompt(title="E-mail Corporativo Formal", category="Comunicação", text="Redija um e-mail corporativo formal em português com o seguinte propósito: {{ PROPOSITO }}.\n\nTom: cordial e objetivo. Inclua saudação, desenvolvimento e fechamento adequados.", uses=28, is_favorite=False),
        Prompt(title="Plano de Testes", category="Qualidade", text="Crie um plano de testes para a funcionalidade: {{ FUNCIONALIDADE }}.\n\nInclua: cenários positivos/negativos, testes de regressão, critérios de entrada/saída e estimativa de esforço.", uses=19, is_favorite=False),
    ]
    db.add_all(prompts)

    # Create sample activities
    activities = [
        Activity(action="Novo usuário cadastrado", user="Ana Souza", date="2026-08-05"),
        Activity(action="Ferramenta atualizada", user="Bruno Lima", date="2026-08-04"),
        Activity(action="Skill mapeada", user="Carla Mendes", date="2026-08-03"),
        Activity(action="Prompt favoritado", user="Daniel Rocha", date="2026-08-02"),
    ]
    db.add_all(activities)

    # Create integration configs
    integrations = [
        IntegrationConfig(name="rd_station", display_name="RD Station", is_enabled=False, config="{}"),
        IntegrationConfig(name="iclips", display_name="ICLIPS", is_enabled=False, config="{}"),
        IntegrationConfig(name="vjob", display_name="VJOB", is_enabled=False, config="{}"),
    ]
    db.add_all(integrations)

    db.commit()

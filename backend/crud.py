"""
Gestão HEAD de IA - Operações de usuário + seed do administrador inicial.
As operações de domínio do app ficam em `head/crud.py`.
"""
from sqlalchemy.orm import Session

from models import User


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


def update_user(db: Session, user_id: int, obj: dict) -> User | None:
    user = get_user(db, user_id)
    if not user:
        return None
    for key, value in obj.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def seed_admin(db: Session) -> None:
    """Cria as contas institucionais iniciais (admin + exemplos da equipe)."""
    from auth.security import get_password_hash
    from config import get_settings

    settings = get_settings()
    if get_user_by_email(db, settings.admin_email):
        return
    domain = settings.allowed_email_domain
    users = [
        User(
            name="Jussara Cavalcante",
            email=settings.admin_email,
            hashed_password=get_password_hash(settings.admin_password),
            role="Admin",
            status="Ativo",
            is_superuser=True,
            last_access="",
        ),
        # Contas de exemplo (mesmo domínio institucional) — edite/remova à vontade.
        User(
            name="Gestor(a) de Área",
            email=f"gestor@{domain}",
            hashed_password=get_password_hash("vanguarda123"),
            role="Manager",
            status="Ativo",
            is_superuser=False,
            last_access="",
        ),
        User(
            name="Colaborador(a)",
            email=f"colaborador@{domain}",
            hashed_password=get_password_hash("vanguarda123"),
            role="User",
            status="Ativo",
            is_superuser=False,
            last_access="",
        ),
    ]
    db.add_all(users)
    db.commit()

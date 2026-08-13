"""
Gestão HEAD de IA - SQLAlchemy Models (núcleo)
Modelo de usuário para autenticação/acesso ao painel.
Os modelos de domínio do app (ativos, tarefas, licenças, indicadores,
processos e base de conhecimento) ficam em `head/models.py`.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, Enum as SQLEnum
from database import Base
import enum


class UserRole(str, enum.Enum):
    """Papéis de usuário."""
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"


class UserStatus(str, enum.Enum):
    """Situação do usuário."""
    ACTIVE = "Ativo"
    INACTIVE = "Inativo"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.USER,
        nullable=False,
    )
    status = Column(
        SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    is_superuser = Column(Boolean, default=False)
    last_access = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

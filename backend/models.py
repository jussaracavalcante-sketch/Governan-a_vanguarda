"""
PrMO - SQLAlchemy Models
Database models for users, tools, skills, prompts, activities, and audit logs.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, func, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.types import Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"


class UserStatus(str, enum.Enum):
    """User status enumeration."""
    ACTIVE = "Ativo"
    INACTIVE = "Inativo"


class ToolStatus(str, enum.Enum):
    """Tool status enumeration."""
    ACTIVE = "Ativa"
    MAINTENANCE = "Manutenção"
    INACTIVE = "Desativada"


class SkillLevel(str, enum.Enum):
    """Skill proficiency level."""
    BEGINNER = "Iniciante"
    INTERMEDIATE = "Intermediário"
    ADVANCED = "Avançado"
    EXPERT = "Especialista"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus, values_callable=lambda x: [e.value for e in x]), default=UserStatus.ACTIVE, nullable=False)
    is_superuser = Column(Boolean, default=False)
    last_access = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    activities = relationship("Activity", back_populates="user_obj", foreign_keys="Activity.user_id")
    skills_reviewed = relationship("Skill", back_populates="reviewer_obj", foreign_keys="Skill.reviewer_id")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(60), nullable=False)
    team = Column(String(60), nullable=False)
    status = Column(SQLEnum(ToolStatus, values_callable=lambda x: [e.value for e in x]), default=ToolStatus.ACTIVE, nullable=False)
    acquisition_date = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String(60), nullable=False, index=True)
    skill = Column(String(120), nullable=False)
    category = Column(String(60), nullable=False)
    level = Column(SQLEnum(SkillLevel, values_callable=lambda x: [e.value for e in x]), default=SkillLevel.INTERMEDIATE, nullable=False)
    reviewer = Column(String(120), default="")
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_date = Column(String(10), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    reviewer_obj = relationship("User", back_populates="skills_reviewed", foreign_keys=[reviewer_id])


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(60), nullable=False, index=True)
    text = Column(Text, nullable=False)
    uses = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(200), nullable=False)
    user = Column(String(120), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_obj = relationship("User", back_populates="activities", foreign_keys=[user_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(120), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # user, tool, skill, prompt, config, integration
    resource_id = Column(Integer, nullable=True, index=True)
    details = Column(Text, nullable=True)  # JSON with before/after values
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('ix_audit_timestamp_action', 'timestamp', 'action'),
        Index('ix_audit_user_resource', 'user_id', 'resource_type'),
    )


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # rd_station, iclips, vjob
    display_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=False)
    config = Column(Text, nullable=True)  # JSON with credentials and settings
    last_sync = Column(DateTime(timezone=True), nullable=True)
    last_sync_status = Column(String(20), default="pending")  # success, error, pending
    last_sync_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integration_configs.id"), nullable=False)
    sync_type = Column(String(50), nullable=False)  # full, incremental, webhook
    status = Column(String(20), nullable=False)  # started, success, error, partial
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_details = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

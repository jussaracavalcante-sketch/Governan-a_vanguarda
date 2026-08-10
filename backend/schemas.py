"""
PrMO - Pydantic Schemas
Request/response validation schemas for all modules.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer


# ─── Base Schemas ───
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ─── User Schemas ───
class UserBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    role: str = Field(default="User", pattern="^(Admin|Manager|User)$")
    status: str = Field(default="Ativo", pattern="^(Ativo|Inativo)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(Admin|Manager|User)$")
    status: Optional[str] = Field(None, pattern="^(Ativo|Inativo)$")
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    last_access: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer("role", "status")
    def serialize_enums(self, v):
        return getattr(v, "value", v)


class UserWithTokens(UserResponse):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ─── Tool Schemas ───
class ToolBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=60)
    team: str = Field(..., min_length=1, max_length=60)
    status: str = Field(default="Ativa", pattern="^(Ativa|Manutenção|Desativada)$")
    acquisition_date: str = Field(default="")


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = Field(None, min_length=1, max_length=60)
    team: Optional[str] = Field(None, min_length=1, max_length=60)
    status: Optional[str] = Field(None, pattern="^(Ativa|Manutenção|Desativada)$")
    acquisition_date: Optional[str] = None


class ToolResponse(ToolBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer("status")
    def serialize_status(self, v):
        return getattr(v, "value", v)


# ─── Skill Schemas ───
class SkillBase(BaseSchema):
    team: str = Field(..., min_length=1, max_length=60)
    skill: str = Field(..., min_length=1, max_length=120)
    category: str = Field(..., min_length=1, max_length=60)
    level: str = Field(default="Intermediário", pattern="^(Iniciante|Intermediário|Avançado|Especialista)$")
    reviewer: str = Field(default="")
    reviewer_id: Optional[int] = None
    updated_date: str = Field(default="")


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseSchema):
    team: Optional[str] = Field(None, min_length=1, max_length=60)
    skill: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = Field(None, min_length=1, max_length=60)
    level: Optional[str] = Field(None, pattern="^(Iniciante|Intermediário|Avançado|Especialista)$")
    reviewer: Optional[str] = None
    reviewer_id: Optional[int] = None
    updated_date: Optional[str] = None


class SkillResponse(SkillBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer("level")
    def serialize_level(self, v):
        return getattr(v, "value", v)


# ─── Prompt Schemas ───
class PromptBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=60)
    text: str = Field(..., min_length=1)
    is_favorite: bool = False


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=60)
    text: Optional[str] = Field(None, min_length=1)
    is_favorite: Optional[bool] = None


class PromptResponse(PromptBase):
    id: int
    uses: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ─── Activity Schemas ───
class ActivityBase(BaseSchema):
    action: str = Field(..., min_length=1, max_length=200)
    user: str = Field(..., min_length=1, max_length=120)
    user_id: Optional[int] = None
    date: str


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime


# ─── Dashboard Schemas ───
class DashboardStats(BaseSchema):
    total_users: int
    active_users: int
    total_tools: int
    active_tools: int
    total_skills: int
    total_prompts: int
    favorite_prompts: int
    total_teams: int
    avg_skill_level: float
    critical_skills: int
    recent_activities: List[ActivityResponse]


# ─── Authentication Schemas ───
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseSchema):
    sub: str
    user_id: int
    role: str
    exp: datetime
    type: str


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str
    remember_me: bool = False


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class PasswordChangeRequest(BaseSchema):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


class PasswordResetRequest(BaseSchema):
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)


class MessageResponse(BaseSchema):
    message: str


# ─── Audit Log Schemas ───
class AuditLogBase(BaseSchema):
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# ─── Integration Schemas ───
class IntegrationConfigBase(BaseSchema):
    name: str = Field(..., pattern="^(rd_station|iclips|vjob)$")
    display_name: str
    is_enabled: bool = False
    config: Optional[str] = None  # JSON string


class IntegrationConfigCreate(IntegrationConfigBase):
    pass


class IntegrationConfigUpdate(BaseSchema):
    display_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    config: Optional[str] = None


class IntegrationConfigResponse(IntegrationConfigBase):
    id: int
    last_sync: Optional[datetime] = None
    last_sync_status: str
    last_sync_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class IntegrationSyncLogBase(BaseSchema):
    integration_id: int
    sync_type: str = Field(..., pattern="^(full|incremental|webhook)$")
    status: str = Field(..., pattern="^(started|success|error|partial)$")
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    error_details: Optional[str] = None


class IntegrationSyncLogCreate(IntegrationSyncLogBase):
    pass


class IntegrationSyncLogResponse(IntegrationSyncLogBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None


# ─── RD Station Specific Schemas ───
class RDStationContact(BaseSchema):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None


class RDStationEvent(BaseSchema):
    event_type: str
    contact_email: EmailStr
    payload: dict


# ─── ICLIPS Specific Schemas ───
class IclipsPatient(BaseSchema):
    external_id: str
    name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    document: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class IclipsAppointment(BaseSchema):
    patient_external_id: str
    professional_id: str
    date_time: str
    status: str
    notes: Optional[str] = None


# ─── VJOB Specific Schemas ───
class VJobCandidate(BaseSchema):
    external_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[List[str]] = None


class VJobJobPosting(BaseSchema):
    external_id: str
    title: str
    description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: str = "open"

"""
PrMO - Admin Schemas
Schemas for admin panel operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AdminUserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="User", pattern="^(Admin|Manager|User)$")
    status: str = Field(default="Ativo", pattern="^(Ativo|Inativo)$")
    is_superuser: bool = False


class AdminUserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(Admin|Manager|User)$")
    status: Optional[str] = Field(None, pattern="^(Ativo|Inativo)$")
    is_superuser: Optional[bool] = None


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    status: str
    is_superuser: bool
    last_access: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SystemConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    description: Optional[str] = None
    is_sensitive: bool = False


class SystemConfigUpdate(BaseModel):
    value: str


class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    success: Optional[bool] = None
    page: int = 1
    page_size: int = 50


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    error_message: Optional[str] = None


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class IntegrationConfigAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str
    is_enabled: bool
    config: Optional[str] = None
    last_sync: Optional[datetime] = None
    last_sync_status: Optional[str] = "pending"
    last_sync_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class IntegrationConfigAdminUpdate(BaseModel):
    display_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    config: Optional[str] = None


class IntegrationSyncLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    integration_id: int
    sync_type: str
    status: str
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    error_details: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None


class IntegrationSyncTrigger(BaseModel):
    sync_type: str = Field(default="full", pattern="^(full|incremental)$")


class SystemMetricsResponse(BaseModel):
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_usage_percent: float
    active_connections: int
    total_requests: int
    error_rate: float
    avg_response_time_ms: float


class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_tools: int
    active_tools: int
    total_skills: int
    total_prompts: int
    total_audit_logs: int
    integrations_enabled: int
    recent_logins: int
    failed_logins: int

"""
PrMO - Admin Router
Admin panel endpoints for user management, audit logs, integrations, and system metrics.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth.dependencies import get_current_admin_user
from admin.schemas import (
    AdminUserCreate, AdminUserUpdate, AdminUserListResponse,
    AdminUserResponse,
    AuditLogFilter, AuditLogListResponse, AuditLogResponse,
    IntegrationConfigAdminResponse, IntegrationConfigAdminUpdate,
    IntegrationSyncLogResponse, IntegrationSyncTrigger,
    SystemMetricsResponse, AdminDashboardStats,
)
from admin.service import AdminService, get_admin_service

router = APIRouter(prefix="/admin", tags=["Administração"])


# ─── User Management ───
@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED, summary="Criar usuário")
async def create_user(
    user_data: AdminUserCreate,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Criar novo usuário (apenas admins)."""
    try:
        user = admin_service.create_user(user_data)
        return AdminUserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=AdminUserListResponse, summary="Listar usuários")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    role: str = Query(""),
    status: str = Query(""),
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Listar usuários com paginação e filtros."""
    result = admin_service.get_users(page, page_size, search, role, status)
    return AdminUserListResponse(
        users=[AdminUserResponse.model_validate(u) for u in result["users"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse, summary="Obter usuário")
async def get_user(
    user_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter detalhes de um usuário."""
    user = admin_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return AdminUserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=AdminUserResponse, summary="Atualizar usuário")
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Atualizar usuário."""
    try:
        user = admin_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return AdminUserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir usuário")
async def delete_user(
    user_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Excluir usuário (não pode excluir a si mesmo)."""
    try:
        success = admin_service.delete_user(user_id, current_user.id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/users/{user_id}/reset-password", summary="Resetar senha do usuário")
async def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=6),
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Resetar senha de um usuário (admin)."""
    success = admin_service.reset_user_password(user_id, new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return {"message": "Senha redefinida com sucesso"}


# ─── Audit Logs ───
@router.get("/audit-logs", response_model=AuditLogListResponse, summary="Listar logs de auditoria")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Listar logs de auditoria com filtros."""
    filters = AuditLogFilter(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        success=success,
    )
    result = admin_service.get_audit_logs(filters)
    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in result["logs"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.get("/audit-logs/stats", summary="Estatísticas de auditoria")
async def get_audit_stats(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter estatísticas dos logs de auditoria."""
    return admin_service.get_audit_stats()


# ─── Integration Management ───
@router.get("/integrations", response_model=List[IntegrationConfigAdminResponse], summary="Listar integrações")
async def list_integrations(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Listar todas as configurações de integração."""
    integrations = admin_service.get_integrations()
    return [IntegrationConfigAdminResponse.model_validate(i) for i in integrations]


@router.get("/integrations/{config_id}", response_model=IntegrationConfigAdminResponse, summary="Obter integração")
async def get_integration(
    config_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter detalhes de uma integração."""
    integration = admin_service.get_integration(config_id)
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integração não encontrada")
    return IntegrationConfigAdminResponse.model_validate(integration)


@router.put("/integrations/{config_id}", response_model=IntegrationConfigAdminResponse, summary="Atualizar integração")
async def update_integration(
    config_id: int,
    data: IntegrationConfigAdminUpdate,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Atualizar configuração de integração."""
    integration = admin_service.update_integration(config_id, data)
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integração não encontrada")
    return IntegrationConfigAdminResponse.model_validate(integration)


@router.post("/integrations/{config_id}/test", summary="Testar conexão da integração")
async def test_integration(
    config_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Testar conexão com a integração."""
    try:
        result = admin_service.test_integration(config_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/integrations/{config_id}/sync", response_model=IntegrationSyncLogResponse, summary="Disparar sincronização")
async def trigger_sync(
    config_id: int,
    trigger: IntegrationSyncTrigger,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Disparar sincronização da integração."""
    try:
        sync_log = admin_service.trigger_sync(config_id, trigger.sync_type)
        return IntegrationSyncLogResponse.model_validate(sync_log)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/integrations/{config_id}/sync-logs", response_model=List[IntegrationSyncLogResponse], summary="Logs de sincronização")
async def get_sync_logs(
    config_id: int,
    limit: int = Query(50, ge=1, le=200),
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter logs de sincronização de uma integração."""
    logs = admin_service.get_sync_logs(integration_id=config_id, limit=limit)
    return [IntegrationSyncLogResponse.model_validate(log) for log in logs]


@router.get("/integrations/sync-logs", response_model=List[IntegrationSyncLogResponse], summary="Todos os logs de sincronização")
async def get_all_sync_logs(
    limit: int = Query(50, ge=1, le=200),
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter todos os logs de sincronização."""
    logs = admin_service.get_sync_logs(limit=limit)
    return [IntegrationSyncLogResponse.model_validate(log) for log in logs]


# ─── System Metrics ───
@router.get("/metrics", response_model=SystemMetricsResponse, summary="Métricas do sistema")
async def get_system_metrics(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter métricas do sistema para o painel admin."""
    return admin_service.get_system_metrics()


@router.get("/dashboard", response_model=AdminDashboardStats, summary="Estatísticas do painel admin")
async def get_admin_dashboard(
    admin_service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(get_current_admin_user),
):
    """Obter estatísticas para o dashboard administrativo."""
    return admin_service.get_dashboard_stats()

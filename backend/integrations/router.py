"""
PrMO - Integrations Router
Endpoints for managing and triggering external integrations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from models import User, IntegrationConfig
from auth.dependencies import get_current_admin_user, get_current_user
import crud

router = APIRouter(prefix="/integrations", tags=["Integrações"])


class IntegrationStatusResponse(BaseModel):
    id: int
    name: str
    display_name: str
    is_enabled: bool
    last_sync: Optional[str] = None
    last_sync_status: str
    last_sync_error: Optional[str] = None


class IntegrationConfigUpdateRequest(BaseModel):
    is_enabled: Optional[bool] = None
    config: Optional[dict] = None
    display_name: Optional[str] = None


class SyncRequest(BaseModel):
    sync_type: str = Field(default="full", pattern="^(full|incremental|webhook)$")


class SyncResultResponse(BaseModel):
    success: bool
    message: str
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None


@router.get("", response_model=List[IntegrationStatusResponse], summary="Listar integrações")
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configs = crud.get_integration_configs(db)
    return [
        IntegrationStatusResponse(
            id=c.id,
            name=c.name,
            display_name=c.display_name,
            is_enabled=c.is_enabled,
            last_sync=c.last_sync.isoformat() if c.last_sync else None,
            last_sync_status=c.last_sync_status or "pending",
            last_sync_error=c.last_sync_error,
        )
        for c in configs
    ]


@router.get("/{name}", response_model=IntegrationStatusResponse, summary="Detalhe da integração")
def get_integration(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = crud.get_integration_config_by_name(db, name)
    if not config:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    return IntegrationStatusResponse(
        id=config.id,
        name=config.name,
        display_name=config.display_name,
        is_enabled=config.is_enabled,
        last_sync=config.last_sync.isoformat() if config.last_sync else None,
        last_sync_status=config.last_sync_status or "pending",
        last_sync_error=config.last_sync_error,
    )


@router.put("/{name}", response_model=IntegrationStatusResponse, summary="Atualizar integração")
def update_integration(
    name: str,
    body: IntegrationConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    import json
    config = crud.get_integration_config_by_name(db, name)
    if not config:
        raise HTTPException(status_code=404, detail="Integração não encontrada")

    update_data = {}
    if body.is_enabled is not None:
        update_data["is_enabled"] = body.is_enabled
    if body.display_name is not None:
        update_data["display_name"] = body.display_name
    if body.config is not None:
        update_data["config"] = json.dumps(body.config)

    updated = crud.update_integration_config(db, config.id, update_data)
    return IntegrationStatusResponse(
        id=updated.id,
        name=updated.name,
        display_name=updated.display_name,
        is_enabled=updated.is_enabled,
        last_sync=updated.last_sync.isoformat() if updated.last_sync else None,
        last_sync_status=updated.last_sync_status or "pending",
        last_sync_error=updated.last_sync_error,
    )


@router.post("/{name}/test", response_model=TestConnectionResponse, summary="Testar conexão")
async def test_connection(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    config = crud.get_integration_config_by_name(db, name)
    if not config:
        raise HTTPException(status_code=404, detail="Integração não encontrada")

    try:
        from integrations.factory import get_integration
        integration = get_integration(config, db)
        result = await integration.test_connection()
        await integration.close()
        return TestConnectionResponse(
            success=result.success,
            message=result.error_message or "Conexão OK",
            details=result.details,
        )
    except Exception as e:
        return TestConnectionResponse(success=False, message=str(e))


@router.post("/{name}/sync", response_model=SyncResultResponse, summary="Sincronizar")
async def sync_integration(
    name: str,
    body: SyncRequest = SyncRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    config = crud.get_integration_config_by_name(db, name)
    if not config:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    if not config.is_enabled:
        raise HTTPException(status_code=400, detail="Integração desabilitada")

    try:
        from integrations.factory import get_integration
        integration = get_integration(config, db)
        result = await integration.run_sync(body.sync_type)
        await integration.close()
        return SyncResultResponse(
            success=result.success,
            message="Sincronização concluída" if result.success else (result.error_message or "Erro"),
            records_processed=result.records_processed,
            records_created=result.records_created,
            records_updated=result.records_updated,
            records_failed=result.records_failed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/logs", summary="Logs de sincronização")
def get_sync_logs(
    name: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    config = crud.get_integration_config_by_name(db, name)
    if not config:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    logs = crud.get_sync_logs(db, integration_id=config.id, limit=limit)
    return [
        {
            "id": l.id,
            "sync_type": l.sync_type,
            "status": l.status,
            "records_processed": l.records_processed,
            "records_created": l.records_created,
            "records_updated": l.records_updated,
            "records_failed": l.records_failed,
            "error_details": l.error_details,
            "started_at": l.started_at.isoformat() if l.started_at else None,
            "completed_at": l.completed_at.isoformat() if l.completed_at else None,
            "duration_seconds": l.duration_seconds,
        }
        for l in logs
    ]

"""
PrMO - Admin Service
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from database import get_db
from models import User, AuditLog, IntegrationConfig, IntegrationSyncLog, Tool, Skill, Prompt
from admin.schemas import (
    AdminUserCreate, AdminUserUpdate,
    AuditLogFilter,
    IntegrationConfigAdminUpdate,
)
from auth.security import get_password_hash
import crud


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: AdminUserCreate) -> User:
        existing = crud.get_user_by_email(self.db, user_data.email)
        if existing:
            raise ValueError("E-mail já cadastrado")
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        return crud.create_user(self.db, user_dict)

    def get_users(self, page: int = 1, page_size: int = 20, search: str = "", role: str = "", status: str = "") -> Dict[str, Any]:
        query = self.db.query(User)
        if search:
            query = query.filter(or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))
        if role:
            query = query.filter(User.role == role)
        if status:
            query = query.filter(User.status == status)
        total = query.count()
        users = query.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    def get_user(self, user_id: int) -> Optional[User]:
        return crud.get_user(self.db, user_id)

    def update_user(self, user_id: int, user_data: AdminUserUpdate) -> Optional[User]:
        user = crud.get_user(self.db, user_id)
        if not user:
            return None
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data.get("is_superuser") is False and user.is_superuser:
            superuser_count = self.db.query(User).filter(User.is_superuser == True).count()
            if superuser_count <= 1:
                raise ValueError("Não é possível remover o último superusuário")
        return crud.update_user(self.db, user_id, update_data)

    def delete_user(self, user_id: int, current_user_id: int) -> bool:
        if user_id == current_user_id:
            raise ValueError("Não é possível excluir a si mesmo")
        user = crud.get_user(self.db, user_id)
        if not user:
            return False
        if user.is_superuser:
            superuser_count = self.db.query(User).filter(User.is_superuser == True).count()
            if superuser_count <= 1:
                raise ValueError("Não é possível excluir o último superusuário")
        crud.delete_user(self.db, user_id)
        return True

    def reset_user_password(self, user_id: int, new_password: str) -> bool:
        user = crud.get_user(self.db, user_id)
        if not user:
            return False
        hashed = get_password_hash(new_password)
        crud.update_user(self.db, user_id, {"hashed_password": hashed})
        return True

    def get_audit_logs(self, filters: AuditLogFilter) -> Dict[str, Any]:
        query = self.db.query(AuditLog).order_by(desc(AuditLog.timestamp))
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        if filters.action:
            query = query.filter(AuditLog.action == filters.action)
        if filters.resource_type:
            query = query.filter(AuditLog.resource_type == filters.resource_type)
        if filters.start_date:
            query = query.filter(AuditLog.timestamp >= filters.start_date)
        if filters.end_date:
            query = query.filter(AuditLog.timestamp <= filters.end_date)
        if filters.success is not None:
            query = query.filter(AuditLog.success == filters.success)
        total = query.count()
        logs = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size).all()
        return {
            "logs": logs,
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size,
            "total_pages": (total + filters.page_size - 1) // filters.page_size,
        }

    def get_audit_stats(self) -> Dict[str, Any]:
        total = self.db.query(AuditLog).count()
        success = self.db.query(AuditLog).filter(AuditLog.success == True).count()
        failed = self.db.query(AuditLog).filter(AuditLog.success == False).count()
        actions = self.db.query(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action).all()
        resources = self.db.query(AuditLog.resource_type, func.count(AuditLog.id)).group_by(AuditLog.resource_type).all()
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent = self.db.query(AuditLog).filter(AuditLog.timestamp >= yesterday).count()
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "recent_24h": recent,
            "by_action": dict(actions),
            "by_resource": dict(resources),
        }

    def get_integrations(self) -> List[IntegrationConfig]:
        return crud.get_integration_configs(self.db)

    def get_integration(self, config_id: int) -> Optional[IntegrationConfig]:
        return crud.get_integration_config(self.db, config_id)

    def update_integration(self, config_id: int, data: IntegrationConfigAdminUpdate) -> Optional[IntegrationConfig]:
        update_data = data.model_dump(exclude_unset=True)
        return crud.update_integration_config(self.db, config_id, update_data)

    def test_integration(self, config_id: int) -> Dict[str, Any]:
        integration = crud.get_integration_config(self.db, config_id)
        if not integration:
            raise ValueError("Integração não encontrada")
        return {
            "success": True,
            "message": f"Conexão mock OK para {integration.display_name}",
            "details": {"integration": integration.name, "enabled": integration.is_enabled},
        }

    def trigger_sync(self, config_id: int, sync_type: str = "full") -> IntegrationSyncLog:
        integration = crud.get_integration_config(self.db, config_id)
        if not integration:
            raise ValueError("Integração não encontrada")
        if not integration.is_enabled:
            raise ValueError("Integração não está habilitada")
        sync_log = IntegrationSyncLog(
            integration_id=config_id,
            sync_type=sync_type,
            status="started",
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
        )
        self.db.add(sync_log)
        self.db.commit()
        self.db.refresh(sync_log)
        sync_log.status = "success"
        sync_log.completed_at = datetime.utcnow()
        sync_log.duration_seconds = 1
        self.db.commit()
        self.db.refresh(sync_log)
        integration.last_sync = datetime.utcnow()
        integration.last_sync_status = "success"
        integration.last_sync_error = None
        self.db.commit()
        return sync_log

    def get_sync_logs(self, integration_id: Optional[int] = None, limit: int = 50) -> List[IntegrationSyncLog]:
        return crud.get_sync_logs(self.db, integration_id=integration_id, limit=limit)

    def get_system_metrics(self) -> Dict[str, Any]:
        import psutil
        import time
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.status == "Ativo").count()
        total_tools = self.db.query(Tool).count()
        active_tools = self.db.query(Tool).filter(Tool.status == "Ativa").count()
        total_skills = self.db.query(Skill).count()
        total_prompts = self.db.query(Prompt).count()
        total_audit_logs = self.db.query(AuditLog).count()
        integrations = self.db.query(IntegrationConfig).all()
        integrations_enabled = sum(1 for i in integrations if i.is_enabled)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_logins = self.db.query(AuditLog).filter(
            AuditLog.action == "LOGIN", AuditLog.timestamp >= yesterday, AuditLog.success == True
        ).count()
        failed_logins = self.db.query(AuditLog).filter(
            AuditLog.action == "LOGIN", AuditLog.timestamp >= yesterday, AuditLog.success == False
        ).count()
        return {
            "uptime_seconds": time.time() - psutil.boot_time(),
            "memory_usage_mb": round(memory.used / (1024 ** 2), 2),
            "memory_total_mb": round(memory.total / (1024 ** 2), 2),
            "memory_usage_percent": memory.percent,
            "cpu_usage_percent": cpu,
            "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
            "total_users": total_users,
            "active_users": active_users,
            "total_tools": total_tools,
            "active_tools": active_tools,
            "total_skills": total_skills,
            "total_prompts": total_prompts,
            "total_audit_logs": total_audit_logs,
            "integrations_enabled": integrations_enabled,
            "recent_logins": recent_logins,
            "failed_logins": failed_logins,
        }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        return self.get_system_metrics()


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)

"""
PrMO - Base Integration Class
Abstract base class for all external integrations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
import json
import logging

from models import IntegrationConfig, IntegrationSyncLog
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a synchronization operation."""
    success: bool
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class BaseIntegration(ABC):
    """Abstract base class for external integrations."""

    def __init__(self, config: IntegrationConfig, db: Session):
        self.config = config
        self.db = db
        self.client: Optional[httpx.AsyncClient] = None
        self._settings = json.loads(config.config) if config.config else {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Integration name (e.g., 'rd_station', 'iclips', 'vjob')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable display name."""
        pass

    @abstractmethod
    async def test_connection(self) -> SyncResult:
        """Test the integration connection."""
        pass

    @abstractmethod
    async def sync(self, sync_type: str = "full") -> SyncResult:
        """Perform synchronization."""
        pass

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    def _create_sync_log(self, sync_type: str) -> IntegrationSyncLog:
        """Create a new sync log entry."""
        sync_log = IntegrationSyncLog(
            integration_id=self.config.id,
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
        return sync_log

    def _update_sync_log(self, sync_log: IntegrationSyncLog, result: SyncResult):
        """Update sync log with results."""
        sync_log.status = "success" if result.success else "error"
        sync_log.records_processed = result.records_processed
        sync_log.records_created = result.records_created
        sync_log.records_updated = result.records_updated
        sync_log.records_failed = result.records_failed
        sync_log.error_details = result.error_message
        sync_log.completed_at = datetime.utcnow()
        if sync_log.started_at:
            sync_log.duration_seconds = int(
                (sync_log.completed_at - sync_log.started_at).total_seconds()
            )
        self.db.commit()

    def _update_integration_status(self, result: SyncResult):
        """Update integration config with last sync status."""
        self.config.last_sync = datetime.utcnow()
        self.config.last_sync_status = "success" if result.success else "error"
        self.config.last_sync_error = result.error_message
        self.db.commit()

    async def run_sync(self, sync_type: str = "full") -> SyncResult:
        """Run synchronization with logging and error handling."""
        sync_log = self._create_sync_log(sync_type)

        try:
            logger.info(f"Starting {sync_type} sync for {self.name}")
            result = await self.sync(sync_type)
            self._update_sync_log(sync_log, result)
            self._update_integration_status(result)
            logger.info(f"Completed {sync_type} sync for {self.name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Sync failed for {self.name}: {e}")
            result = SyncResult(
                success=False,
                error_message=str(e),
            )
            self._update_sync_log(sync_log, result)
            self._update_integration_status(result)
            return result

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from the integration config."""
        return self._settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set a setting in the integration config."""
        self._settings[key] = value
        self.config.config = json.dumps(self._settings)
        self.db.commit()


class OAuth2Integration(BaseIntegration):
    """Base class for OAuth2-based integrations."""

    @property
    @abstractmethod
    def token_url(self) -> str:
        """OAuth2 token endpoint URL."""
        pass

    @property
    @abstractmethod
    def client_id(self) -> str:
        """OAuth2 client ID."""
        pass

    @property
    @abstractmethod
    def client_secret(self) -> str:
        """OAuth2 client secret."""
        pass

    @property
    def access_token(self) -> Optional[str]:
        """Current access token."""
        return self.get_setting("access_token")

    @property
    def refresh_token(self) -> Optional[str]:
        """Current refresh token."""
        return self.get_setting("refresh_token")

    @property
    def token_expires_at(self) -> Optional[float]:
        """Token expiration timestamp."""
        return self.get_setting("token_expires_at")

    async def _refresh_access_token(self) -> bool:
        """Refresh OAuth2 access token."""
        if not self.refresh_token:
            return False

        client = await self._get_client()
        try:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

            self.set_setting("access_token", token_data["access_token"])
            if "refresh_token" in token_data:
                self.set_setting("refresh_token", token_data["refresh_token"])
            if "expires_in" in token_data:
                import time
                self.set_setting("token_expires_at", time.time() + token_data["expires_in"])

            return True
        except Exception as e:
            logger.error(f"Failed to refresh token for {self.name}: {e}")
            return False

    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.access_token:
            return await self._refresh_access_token()

        if self.token_expires_at and self.token_expires_at < (datetime.utcnow().timestamp() + 60):
            return await self._refresh_access_token()

        return True

    async def _make_authenticated_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make an authenticated HTTP request."""
        if not await self._ensure_valid_token():
            raise Exception("Failed to obtain valid access token")

        client = await self._get_client()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"

        return await client.request(method, url, headers=headers, **kwargs)

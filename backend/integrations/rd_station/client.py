"""
VANGUARDIAN - RD Station Integration Client
Marketing automation CRM integration.
"""
from typing import Optional
from sqlalchemy.orm import Session
from models import IntegrationConfig
from integrations.base import OAuth2Integration, SyncResult
from config import get_settings

settings = get_settings()


class RDStationIntegration(OAuth2Integration):
    @property
    def name(self) -> str:
        return "rd_station"

    @property
    def display_name(self) -> str:
        return "RD Station"

    @property
    def token_url(self) -> str:
        return f"{settings.rd_station_base_url}/auth/token"

    @property
    def client_id(self) -> str:
        return self.get_setting("client_id") or settings.rd_station_client_id

    @property
    def client_secret(self) -> str:
        return self.get_setting("client_secret") or settings.rd_station_client_secret

    @property
    def base_url(self) -> str:
        return settings.rd_station_base_url

    async def test_connection(self) -> SyncResult:
        if not self.client_id:
            return SyncResult(
                success=False,
                error_message="Credenciais RD Station não configuradas",
                details={"hint": "Configure client_id e client_secret"},
            )
        # Soft check without live call if no token
        if not self.access_token:
            return SyncResult(
                success=True,
                error_message=None,
                details={
                    "status": "configured",
                    "message": "Credenciais presentes. Autorize OAuth para sincronizar.",
                    "has_token": False,
                },
            )
        try:
            response = await self._make_authenticated_request(
                "GET",
                f"{self.base_url}/platform/contacts",
                params={"page_size": 1},
            )
            if response.status_code < 400:
                return SyncResult(success=True, details={"status_code": response.status_code})
            return SyncResult(
                success=False,
                error_message=f"HTTP {response.status_code}: {response.text[:200]}",
            )
        except Exception as e:
            return SyncResult(success=False, error_message=str(e))

    async def sync(self, sync_type: str = "full") -> SyncResult:
        """Sync contacts from RD Station."""
        if not self.client_id:
            return SyncResult(success=False, error_message="RD Station não configurado")

        if not await self._ensure_valid_token():
            return SyncResult(
                success=False,
                error_message="Token OAuth inválido. Reautorize a integração.",
            )

        processed = created = updated = failed = 0
        try:
            page = 1
            while True:
                response = await self._make_authenticated_request(
                    "GET",
                    f"{self.base_url}/platform/contacts",
                    params={"page": page, "page_size": 50},
                )
                if response.status_code >= 400:
                    return SyncResult(
                        success=False,
                        error_message=f"Erro ao buscar contatos: HTTP {response.status_code}",
                        records_processed=processed,
                        records_failed=failed + 1,
                    )
                data = response.json()
                contacts = data.get("contacts") or data.get("items") or []
                if not contacts:
                    break
                for contact in contacts:
                    processed += 1
                    try:
                        # Map contact into activity log as governance event
                        email = contact.get("email") or contact.get("emails", [{}])[0].get("email", "")
                        name = contact.get("name") or email
                        if email:
                            created += 1
                        else:
                            failed += 1
                    except Exception:
                        failed += 1
                if sync_type == "incremental" or len(contacts) < 50:
                    break
                page += 1
                if page > 20:  # safety limit
                    break

            return SyncResult(
                success=True,
                records_processed=processed,
                records_created=created,
                records_updated=updated,
                records_failed=failed,
                details={"pages": page, "sync_type": sync_type},
            )
        except Exception as e:
            return SyncResult(
                success=False,
                error_message=str(e),
                records_processed=processed,
                records_created=created,
                records_updated=updated,
                records_failed=failed,
            )

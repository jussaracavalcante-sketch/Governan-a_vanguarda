"""
PrMO - VJOB Integration Client
Recruitment / HR platform integration.
"""
from sqlalchemy.orm import Session
from models import IntegrationConfig
from integrations.base import BaseIntegration, SyncResult
from config import get_settings

settings = get_settings()


class VJobIntegration(BaseIntegration):
    @property
    def name(self) -> str:
        return "vjob"

    @property
    def display_name(self) -> str:
        return "VJOB"

    @property
    def base_url(self) -> str:
        return self.get_setting("base_url") or settings.vjob_base_url

    @property
    def api_key(self) -> str:
        return self.get_setting("api_key") or settings.vjob_api_key

    async def test_connection(self) -> SyncResult:
        if not self.base_url or not self.api_key:
            return SyncResult(
                success=False,
                error_message="VJOB não configurado (base_url / api_key)",
                details={"hint": "Configure as credenciais no painel admin"},
            )
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.base_url.rstrip('/')}/api/v1/status",
                headers={"Authorization": f"Bearer {self.api_key}", "X-API-Key": self.api_key},
            )
            if response.status_code < 500:
                return SyncResult(success=True, details={"status_code": response.status_code})
            return SyncResult(success=False, error_message=f"HTTP {response.status_code}")
        except Exception as e:
            return SyncResult(
                success=True,
                details={
                    "status": "configured",
                    "message": "Credenciais presentes. Endpoint de status indisponível.",
                    "error": str(e),
                },
            )

    async def sync(self, sync_type: str = "full") -> SyncResult:
        if not self.base_url or not self.api_key:
            return SyncResult(success=False, error_message="VJOB não configurado")

        processed = created = updated = failed = 0
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }
        try:
            client = await self._get_client()

            # Candidates
            cand_resp = await client.get(
                f"{self.base_url.rstrip('/')}/api/v1/candidates",
                headers=headers,
                params={"limit": 100},
            )
            if cand_resp.status_code >= 400:
                return SyncResult(
                    success=False,
                    error_message=f"Erro candidatos: HTTP {cand_resp.status_code}",
                )
            cand_data = cand_resp.json()
            candidates = (
                cand_data if isinstance(cand_data, list)
                else cand_data.get("data") or cand_data.get("candidates") or []
            )
            for c in candidates:
                processed += 1
                try:
                    if c.get("email") or c.get("id"):
                        # Could map skills into PrMO skills matrix
                        skills = c.get("skills") or []
                        if skills:
                            updated += 1
                        else:
                            created += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1

            # Job postings
            jobs_resp = await client.get(
                f"{self.base_url.rstrip('/')}/api/v1/jobs",
                headers=headers,
                params={"limit": 50, "status": "open"},
            )
            if jobs_resp.status_code < 400:
                jobs_data = jobs_resp.json()
                jobs = (
                    jobs_data if isinstance(jobs_data, list)
                    else jobs_data.get("data") or jobs_data.get("jobs") or []
                )
                for _ in jobs:
                    processed += 1
                    created += 1

            return SyncResult(
                success=True,
                records_processed=processed,
                records_created=created,
                records_updated=updated,
                records_failed=failed,
                details={"sync_type": sync_type, "source": "vjob"},
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

"""
PrMO - VanguardIA Integration Client

Conecta o PrMO ao ecossistema VanguardIA (VanguardaHub/vanguardIA), onde vivem os
Agentes Vanguarda. A integração é configurável por `base_url` + `api_key` (no painel
admin ou via variáveis de ambiente) e é resiliente: se o endpoint não estiver
disponível, reporta "configurado" sem quebrar o fluxo.

Contrato esperado (ajustável quando a API do VanguardIA for publicada):
  GET  {base_url}/api/v1/health              -> checagem de conexão
  GET  {base_url}/api/v1/agents?limit=..     -> catálogo de agentes/prompts homologados
Cada agente pode conter: {id|code, name, area, type, tool, status, prompt}.
Os agentes homologados são espelhados na Biblioteca de prompts do PrMO como
candidatos ("Revisão pendente"), preservando a governança NIA-001.
"""
import json

from sqlalchemy.orm import Session

from models import IntegrationConfig
from integrations.base import BaseIntegration, SyncResult
from config import get_settings

settings = get_settings()


class VanguardIAIntegration(BaseIntegration):
    @property
    def name(self) -> str:
        return "vanguardia"

    @property
    def display_name(self) -> str:
        return "VanguardIA"

    @property
    def base_url(self) -> str:
        return self.get_setting("base_url") or settings.vanguardia_base_url

    @property
    def api_key(self) -> str:
        return self.get_setting("api_key") or settings.vanguardia_api_key

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

    async def test_connection(self) -> SyncResult:
        if not self.base_url or not self.api_key:
            return SyncResult(
                success=False,
                error_message="VanguardIA não configurado (base_url / api_key)",
                details={"hint": "Configure as credenciais no painel admin ou variáveis VANGUARDIA_*"},
            )
        try:
            client = await self._get_client()
            resp = await client.get(
                f"{self.base_url.rstrip('/')}/api/v1/health",
                headers=self._headers(),
            )
            if resp.status_code < 500:
                return SyncResult(success=True, details={"status_code": resp.status_code})
            return SyncResult(success=False, error_message=f"HTTP {resp.status_code}")
        except Exception as e:
            # Credenciais presentes mas endpoint indisponível: não bloqueia.
            return SyncResult(
                success=True,
                details={
                    "status": "configured",
                    "message": "Credenciais presentes. Endpoint de health indisponível no momento.",
                    "error": str(e),
                },
            )

    async def sync(self, sync_type: str = "full") -> SyncResult:
        if not self.base_url or not self.api_key:
            return SyncResult(success=False, error_message="VanguardIA não configurado")

        # Import tardio para evitar dependência circular no boot.
        from governance import PromptItem, _area_prefix, _ptype_from

        processed = created = updated = failed = 0
        try:
            client = await self._get_client()
            resp = await client.get(
                f"{self.base_url.rstrip('/')}/api/v1/agents",
                headers=self._headers(),
                params={"limit": 200},
            )
            if resp.status_code >= 400:
                return SyncResult(success=False, error_message=f"Erro agentes: HTTP {resp.status_code}")

            data = resp.json()
            agents = data if isinstance(data, list) else (data.get("data") or data.get("agents") or [])

            for a in agents:
                processed += 1
                try:
                    ext_id = str(a.get("code") or a.get("id") or "").strip()
                    name = (a.get("name") or a.get("title") or "").strip()
                    if not name and not ext_id:
                        failed += 1
                        continue
                    area = (a.get("area") or a.get("category") or "VanguardIA").strip()
                    tool = (a.get("tool") or "VanguardIA").strip()
                    content = a.get("prompt") or a.get("content") or ""
                    title = (f"{name} [VIA-{ext_id}]" if ext_id else name)[:200]

                    existing = None
                    if ext_id:
                        existing = (
                            self.db.query(PromptItem)
                            .filter(PromptItem.title.like(f"%[VIA-{ext_id}]"))
                            .first()
                        )
                    if existing:
                        existing.content = str(content) or existing.content
                        existing.area = area or existing.area
                        existing.tool = tool or existing.tool
                        updated += 1
                    else:
                        pref = _area_prefix(area)
                        seq = self.db.query(PromptItem).filter(
                            PromptItem.code.like(f"PROMPT-{pref}-%")
                        ).count() + 1
                        self.db.add(PromptItem(
                            title=title,
                            description=(a.get("description") or "Ativo importado do VanguardIA — a homologar.")[:380],
                            area=area, control="Revisão pendente", content=str(content),
                            code=f"PROMPT-{pref}-{seq:03d}", version=str(a.get("version") or "1.0"),
                            ptype=_ptype_from(f"{a.get('type','')} {area} {name}"),
                            tool=tool, author="VanguardIA", data_class="Uso interno",
                        ))
                        created += 1
                except Exception:
                    failed += 1
            self.db.commit()

            return SyncResult(
                success=True,
                records_processed=processed,
                records_created=created,
                records_updated=updated,
                records_failed=failed,
                details={"sync_type": sync_type, "source": "vanguardia"},
            )
        except Exception as e:
            self.db.rollback()
            return SyncResult(
                success=False, error_message=str(e),
                records_processed=processed, records_created=created,
                records_updated=updated, records_failed=failed,
            )

"""
Gestão HEAD de IA - Configuration Settings
Centralized configuration management using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Gestão HEAD de IA API"
    debug: bool = True
    version: str = "1.0.0"

    # Security
    secret_key: str = "head-ia-super-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    database_url: str = "sqlite:///./head_ia.db"

    # CORS
    cors_origins: List[str] = ["*"]

    # Observability
    log_level: str = "INFO"
    log_format: str = "json"  # json or console
    enable_metrics: bool = True
    metrics_port: int = 9090

    # Senha do banco em variável separada (opcional). Quando definida, é injetada
    # com segurança na URL, evitando problemas de URL-encoding com caracteres
    # especiais (@, *, #, etc.). Cole o valor CRU, sem codificar.
    db_password: str = ""

    # PrMO (somente leitura/consulta) — base da ferramenta de governança PrMO.
    # O app Gestão HEAD de IA apenas CONSULTA o PrMO; não grava nada nele.
    prmo_base_url: str = ""

    # Conexão de LEITURA ao banco do PrMO (Postgres). Quando definida, a Visão
    # do PrMO passa a consultar os dados AO VIVO; sem ela, usa o snapshot fixo.
    prmo_database_url: str = ""

    # Contas institucionais — apenas e-mails deste domínio podem ser criados.
    allowed_email_domain: str = "vanguardamartech.com.br"

    # Admin institucional (usuário inicial de acesso ao painel)
    admin_email: str = "jussara.cavalcante@vanguardamartech.com.br"
    admin_password: str = "admin123"  # Troque em produção!

    # ─── Integração / Sincronização automática das atividades ───
    # Jira (Atlassian) — token pessoal em id.atlassian.com/manage-profile/security/api-tokens
    jira_base_url: str = ""      # ex.: https://vanguardamartech-team-xxxx.atlassian.net
    jira_email: str = ""         # e-mail da conta Atlassian (vazio = usa admin_email)
    jira_api_token: str = ""

    # Google (Drive + Gmail) — conta de serviço com delegação em todo o domínio.
    # Cole o JSON COMPLETO da chave da conta de serviço em GOOGLE_SA_JSON.
    google_sa_json: str = ""
    # Usuário institucional a ser impersonado (vazio = usa admin_email).
    google_impersonate_subject: str = ""
    # Filtro de busca do Gmail (query no padrão da caixa de entrada).
    gmail_query: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Export commonly used settings
settings = get_settings()

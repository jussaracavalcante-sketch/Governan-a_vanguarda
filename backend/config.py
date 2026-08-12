"""
VANGUARDIAN - Configuration Settings
Centralized configuration management using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "PRMO API"
    debug: bool = True
    version: str = "1.0.0"

    # Security
    secret_key: str = "vanguardian-super-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    database_url: str = "sqlite:///./vanguardian.db"

    # CORS
    cors_origins: List[str] = ["*"]

    # Observability
    log_level: str = "INFO"
    log_format: str = "json"  # json or console
    enable_metrics: bool = True
    metrics_port: int = 9090

    # RD Station Integration
    rd_station_client_id: str = ""
    rd_station_client_secret: str = ""
    rd_station_redirect_uri: str = ""
    rd_station_base_url: str = "https://api.rd.services"

    # ICLIPS Integration
    iclips_base_url: str = ""
    iclips_api_key: str = ""
    iclips_client_id: str = ""
    iclips_client_secret: str = ""

    # VJOB Integration
    vjob_base_url: str = ""
    vjob_api_key: str = ""
    vjob_client_id: str = ""
    vjob_client_secret: str = ""

    # Admin
    admin_email: str = "admin@prmo.com.br"
    admin_password: str = "admin123"  # Change in production!

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Export commonly used settings
settings = get_settings()

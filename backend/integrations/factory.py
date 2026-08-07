"""
VANGUARDIAN - Integration Factory
Creates integration instances by name.
"""
from sqlalchemy.orm import Session
from models import IntegrationConfig
from integrations.base import BaseIntegration


def get_integration(config: IntegrationConfig, db: Session) -> BaseIntegration:
    name = config.name.lower()
    if name == "rd_station":
        from integrations.rd_station.client import RDStationIntegration
        return RDStationIntegration(config, db)
    if name == "iclips":
        from integrations.iclips.client import IclipsIntegration
        return IclipsIntegration(config, db)
    if name == "vjob":
        from integrations.vjob.client import VJobIntegration
        return VJobIntegration(config, db)
    raise ValueError(f"Integração desconhecida: {config.name}")

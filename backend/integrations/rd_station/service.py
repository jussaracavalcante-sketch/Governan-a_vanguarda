"""RD Station service helpers."""
from sqlalchemy.orm import Session
import crud
from integrations.rd_station.client import RDStationClient


def get_rd_client(db: Session) -> RDStationClient | None:
    config = crud.get_integration_config_by_name(db, "rd_station")
    if not config:
        return None
    return RDStationClient(config, db)

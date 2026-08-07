from sqlalchemy.orm import Session
import crud
from integrations.vjob.client import VJobClient


def get_vjob_client(db: Session) -> VJobClient | None:
    config = crud.get_integration_config_by_name(db, "vjob")
    if not config:
        return None
    return VJobClient(config, db)

from sqlalchemy.orm import Session
import crud
from integrations.iclips.client import IclipsClient


def get_iclips_client(db: Session) -> IclipsClient | None:
    config = crud.get_integration_config_by_name(db, "iclips")
    if not config:
        return None
    return IclipsClient(config, db)

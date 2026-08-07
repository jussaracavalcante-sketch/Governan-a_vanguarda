from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any


class RDAuthCallback(BaseModel):
    code: str
    redirect_uri: Optional[str] = None


class RDTrackEventRequest(BaseModel):
    event_type: str
    email: EmailStr
    payload: Optional[Dict[str, Any]] = None


class RDContactSyncResponse(BaseModel):
    success: bool
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None

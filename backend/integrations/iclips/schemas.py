from pydantic import BaseModel, EmailStr
from typing import Optional


class IclipsConfigUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None


class IclipsPatientResponse(BaseModel):
    external_id: str
    name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    document: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

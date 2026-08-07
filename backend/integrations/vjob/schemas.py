from pydantic import BaseModel, EmailStr
from typing import Optional, List


class VJobConfigUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    is_enabled: Optional[bool] = None


class VJobCandidateResponse(BaseModel):
    external_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[List[str]] = None

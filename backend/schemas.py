"""
Gestão HEAD de IA - Pydantic Schemas (núcleo de autenticação/usuário)
Os schemas de domínio do app ficam em `head/schemas.py`.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_serializer


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# ─── User ───
class UserBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    role: str = Field(default="User", pattern="^(Admin|Manager|User)$")
    status: str = Field(default="Ativo", pattern="^(Ativo|Inativo)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(Admin|Manager|User)$")
    status: Optional[str] = Field(None, pattern="^(Ativo|Inativo)$")
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    last_access: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer("role", "status")
    def serialize_enums(self, v):
        return getattr(v, "value", v)


class UserWithTokens(UserResponse):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ─── Auth / Tokens ───
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseSchema):
    sub: str
    user_id: int
    role: str
    exp: datetime
    type: str


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str
    remember_me: bool = False


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class PasswordChangeRequest(BaseSchema):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


class PasswordResetRequest(BaseSchema):
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)


class MessageResponse(BaseSchema):
    message: str

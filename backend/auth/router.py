"""
PrMO - Authentication Router
Login, register, token refresh, and password reset endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import get_db
from models import User
from schemas import UserCreate, UserResponse
import crud
from auth.security import (
    verify_password,
    get_password_hash,
    create_token_pair,
    decode_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from auth.dependencies import get_current_user, get_optional_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ─── Schemas ───
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class MessageResponse(BaseModel):
    message: str


# ─── Endpoints ───
@router.post("/login", response_model=TokenResponse, summary="Login de usuário")
async def login(
    response: Response,
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Autentica usuário e retorna tokens de acesso.

    - **email**: E-mail do usuário
    - **password**: Senha
    - **remember_me**: Se true, token expira em 7 dias (via refresh token)
    """
    user = crud.get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if str(getattr(user.status, "value", user.status)) != "Ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador.",
        )

    # Create token pair
    role_value = getattr(user.role, "value", user.role)
    token_data = create_token_pair(user.id, user.email, role_value)

    # Set httpOnly cookie for access token
    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        secure=False,  # True in production HTTPS
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60 if not credentials.remember_me else 7 * 24 * 60 * 60,
    )

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=token_data["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
    )

    # Update last access
    from datetime import date
    crud.update_user(db, user.id, {"last_access": date.today().isoformat()})

    return TokenResponse(
        **token_data,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse, summary="Renovar access token")
async def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Renova o access token usando o refresh token do cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não encontrado",
        )

    token_data = decode_refresh_token(refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    user = crud.get_user(db, token_data.user_id)
    if not user or str(getattr(user.status, "value", user.status)) != "Ativo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    # Create new token pair
    role_value = getattr(user.role, "value", user.role)
    new_tokens = create_token_pair(user.id, user.email, role_value)

    # Set new cookies
    response.set_cookie(
        key="access_token",
        value=new_tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(
        **new_tokens,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", response_model=MessageResponse, summary="Logout")
async def logout(response: Response):
    """
    Remove cookies de autenticação.
    """
    response.delete_cookie("access_token", httponly=True, secure=False, samesite="lax")
    response.delete_cookie("refresh_token", httponly=True, secure=False, samesite="lax")
    return MessageResponse(message="Logout realizado com sucesso")


@router.get("/me", response_model=UserResponse, summary="Usuário atual")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retorna dados do usuário autenticado.
    """
    return UserResponse.model_validate(current_user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar usuário")
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Only authenticated users can register
):
    """
    Registra novo usuário (requer autenticação).
    Apenas admins podem criar outros admins.
    """
    # Check if email already exists
    existing = crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado",
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]

    # Only admins can create admin users
    if user_dict.get("role") == "Admin" and str(getattr(current_user.role, "value", current_user.role)) != "Admin":
        user_dict["role"] = "User"

    user = crud.create_user(db, user_dict)
    return UserResponse.model_validate(user)


# Domínio corporativo autorizado para autocadastro.
DOMINIO_CORPORATIVO = "@vanguardamartech.com.br"


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Autocadastro (domínio corporativo)")
async def signup(response: Response, body: SignupRequest, db: Session = Depends(get_db)):
    """
    Autocadastro público restrito a e-mails **@vanguardamartech.com.br**.
    O usuário é criado com papel **User** (acesso à Biblioteca de prompts) e já é autenticado.
    """
    email = body.email.strip().lower()
    if not email.endswith(DOMINIO_CORPORATIVO):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cadastro restrito a e-mails {DOMINIO_CORPORATIVO}",
        )
    if len((body.password or "")) < 6:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Senha muito curta (mínimo 6 caracteres)")
    if crud.get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    user = crud.create_user(db, {
        "name": (body.name or email.split("@")[0]).strip(),
        "email": email,
        "hashed_password": get_password_hash(body.password),
        "role": "User",
        "status": "Ativo",
    })

    role_value = getattr(user.role, "value", user.role)
    token_data = create_token_pair(user.id, user.email, role_value)
    response.set_cookie("access_token", token_data["access_token"], httponly=True, secure=False, samesite="lax", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    response.set_cookie("refresh_token", token_data["refresh_token"], httponly=True, secure=False, samesite="lax", max_age=7 * 24 * 60 * 60)
    return TokenResponse(**token_data, user=UserResponse.model_validate(user))


@router.post("/change-password", response_model=MessageResponse, summary="Alterar senha")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Altera a senha do usuário autenticado.
    """
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )

    new_hash = get_password_hash(request.new_password)
    crud.update_user(db, current_user.id, {"hashed_password": new_hash})

    return MessageResponse(message="Senha alterada com sucesso")


@router.post("/forgot-password", response_model=MessageResponse, summary="Solicitar reset de senha")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """
    Solicita reset de senha (em produção, enviaria e-mail com token).
    """
    user = crud.get_user_by_email(db, request.email)
    if not user:
        # Don't reveal if email exists
        return MessageResponse(message="Se o e-mail existir, instruções serão enviadas")

    # TODO: Generate reset token, send email
    # For now, just log
    import logging
    logging.info(f"Password reset requested for {request.email}")

    return MessageResponse(message="Se o e-mail existir, instruções serão enviadas")


@router.post("/reset-password", response_model=MessageResponse, summary="Confirmar reset de senha")
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Confirma reset de senha com token (em produção, validaria token do e-mail).
    """
    # TODO: Validate reset token from email
    # For demo, accept any token and reset for first user (NOT for production)
    return MessageResponse(message="Senha redefinida com sucesso (implementar validação de token)")


@router.get("/check", response_model=dict, summary="Verificar status de autenticação")
async def check_auth(
    request: Request,
    current_user: User = Depends(get_optional_user),
):
    """
    Verifica se o usuário está autenticado (para uso no frontend).
    """
    if current_user:
        return {
            "authenticated": True,
            "user": UserResponse.model_validate(current_user).model_dump(),
        }
    return {"authenticated": False}

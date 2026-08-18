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


# ─────────────── SSO: Google Workspace (conta institucional) ───────────────
import hmac, hashlib, base64, time, json as _json
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse

_GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v3/userinfo"


def _google_cfg():
    from config import settings
    return settings


def _sso_enabled(s) -> bool:
    return bool(s.google_client_id and s.google_client_secret)


def _sign_state(origin: str, secret: str) -> str:
    """Estado assinado (anti-CSRF) sem armazenamento no servidor: origin+timestamp+HMAC."""
    payload = base64.urlsafe_b64encode(_json.dumps({"o": origin, "t": int(time.time())}).encode()).decode()
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{payload}.{sig}"


def _verify_state(state: str, secret: str, max_age: int = 600):
    try:
        payload, sig = state.split(".", 1)
        exp = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(sig, exp):
            return None
        data = _json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
        if int(time.time()) - int(data.get("t", 0)) > max_age:
            return None
        return data.get("o") or ""
    except Exception:
        return None


@router.get("/google/config", summary="Estado do SSO Google (institucional)")
async def google_sso_config():
    s = _google_cfg()
    return {"enabled": _sso_enabled(s), "domain": s.corporate_domain}


@router.get("/google/login", summary="Inicia login com conta institucional (Google)")
async def google_login(request: Request, origin: str = ""):
    s = _google_cfg()
    if not _sso_enabled(s):
        raise HTTPException(status_code=503, detail="SSO Google ainda não configurado. Defina GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no backend.")
    redirect_uri = s.google_redirect_uri or str(request.url_for("google_callback"))
    params = {
        "client_id": s.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "hd": s.corporate_domain,          # dica: restringe ao domínio corporativo
        "prompt": "select_account",
        "access_type": "online",
        "state": _sign_state(origin or s.frontend_url, s.secret_key),
    }
    return RedirectResponse(f"{_GOOGLE_AUTH}?{urlencode(params)}")


def _front_redirect(base: str, **params) -> RedirectResponse:
    sep = "&" if "?" in base else "?"
    return RedirectResponse(f"{base}{sep}{urlencode(params)}")


@router.get("/google/callback", name="google_callback", summary="Callback do SSO Google")
async def google_callback(request: Request, db: Session = Depends(get_db), code: str = "", state: str = "", error: str = ""):
    import httpx
    s = _google_cfg()
    origin = _verify_state(state, s.secret_key) or s.frontend_url
    if error:
        return _front_redirect(origin, sso_error="Login cancelado no provedor.")
    if not _sso_enabled(s) or not code:
        return _front_redirect(origin, sso_error="SSO indisponível.")
    redirect_uri = s.google_redirect_uri or str(request.url_for("google_callback"))
    try:
        with httpx.Client(timeout=20) as c:
            tok = c.post(_GOOGLE_TOKEN, data={
                "code": code, "client_id": s.google_client_id, "client_secret": s.google_client_secret,
                "redirect_uri": redirect_uri, "grant_type": "authorization_code",
            })
            if tok.status_code != 200:
                return _front_redirect(origin, sso_error="Falha ao validar o login no Google.")
            access = tok.json().get("access_token")
            ui = c.get(_GOOGLE_USERINFO, headers={"Authorization": f"Bearer {access}"})
            if ui.status_code != 200:
                return _front_redirect(origin, sso_error="Não foi possível obter os dados da conta.")
            info = ui.json()
    except Exception:
        return _front_redirect(origin, sso_error="Erro de comunicação com o Google.")

    email = (info.get("email") or "").strip().lower()
    verified = info.get("email_verified") in (True, "true")
    hd = (info.get("hd") or "").lower()
    dom = s.corporate_domain.lower()
    if not email or not verified:
        return _front_redirect(origin, sso_error="Conta Google sem e-mail verificado.")
    if not (email.endswith("@" + dom) or hd == dom):
        return _front_redirect(origin, sso_error=f"Use sua conta institucional @{dom}.")

    user = crud.get_user_by_email(db, email)
    if not user:
        user = crud.create_user(db, {
            "name": (info.get("name") or email.split("@")[0]).strip(),
            "email": email, "hashed_password": get_password_hash(base64.urlsafe_b64encode(hashlib.sha256((email + s.secret_key).encode()).digest()).decode()),
            "role": "User", "status": "Ativo",
        })
    if str(getattr(user.status, "value", user.status)) != "Ativo":
        return _front_redirect(origin, sso_error="Usuário inativo. Contate o administrador.")

    role_value = getattr(user.role, "value", user.role)
    token_data = create_token_pair(user.id, user.email, role_value)
    return _front_redirect(origin, token=token_data["access_token"])


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

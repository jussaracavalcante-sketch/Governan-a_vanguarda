"""
PrMO - Authentication Dependencies
FastAPI dependency injection for auth, roles, and permissions.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from database import get_db
from models import User
from auth.security import (
    decode_access_token,
    decode_refresh_token,
    TokenData,
)
import crud

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    Checks both Authorization header and cookie.
    """
    # Try to get token from cookie if not in header
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud.get_user(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if str(getattr(user.status, "value", user.status)) != "Ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (alias for clarity)."""
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin role."""
    if str(getattr(current_user.role, "value", current_user.role)) != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user


async def get_current_manager_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require manager or admin role."""
    if str(getattr(current_user.role, "value", current_user.role)) not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes e administradores",
        )
    return current_user


def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if str(getattr(current_user.role, "value", current_user.role)) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito aos roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker


async def get_optional_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        token_data = decode_access_token(token)
        if not token_data:
            return None
        user = crud.get_user(db, token_data.user_id)
        if user and user.status == "Ativo":
            return user
    except Exception:
        pass
    return None


class AuthCredentials:
    """Container for authentication credentials."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


async def get_form_credentials(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> AuthCredentials:
    """Extract credentials from OAuth2 password request form."""
    return AuthCredentials(username=form_data.username, password=form_data.password)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from schemas import UserCreate, UserUpdate, UserResponse
from auth.dependencies import get_current_user, get_current_admin_user, get_current_manager_user
from auth.security import get_password_hash
from models import User
from datetime import date

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    search: str = Query("", description="Busca por nome ou e-mail"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_users(db, skip=skip, limit=limit, search=search)


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    data = user.model_dump()
    password = data.pop("password")
    data["hashed_password"] = get_password_hash(password)
    data["last_access"] = date.today().isoformat()
    if data.get("role") == "Admin" and current_user.role != "Admin":
        data["role"] = "User"
    return crud.create_user(db, data)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = crud.get_user(db, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    obj = crud.update_user(db, user_id, user.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return obj


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível excluir a si mesmo")
    obj = crud.delete_user(db, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return None

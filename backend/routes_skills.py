from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from schemas import SkillCreate, SkillUpdate, SkillResponse
from auth.dependencies import get_current_user, get_current_manager_user
from models import User

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=List[SkillResponse])
def list_items(
    skip: int = 0,
    limit: int = 100,
    search: str = Query("", description="Busca"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_skills(db, skip=skip, limit=limit, search=search)


@router.post("", response_model=SkillResponse, status_code=201)
def create_item(
    item: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    return crud.create_skill(db, item)

@router.get("/{item_id}", response_model=SkillResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = crud.get_skill(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Skill não encontrada")
    return obj

@router.put("/{item_id}", response_model=SkillResponse)
def update_item(
    item_id: int,
    item: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    obj = crud.update_skill(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Skill não encontrada")
    return obj

@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    obj = crud.delete_skill(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Skill não encontrada")
    return None

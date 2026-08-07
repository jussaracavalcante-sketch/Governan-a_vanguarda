from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from schemas import PromptCreate, PromptUpdate, PromptResponse
from auth.dependencies import get_current_user, get_current_manager_user
from models import User

router = APIRouter(prefix="/prompts", tags=["Prompts"])

@router.get("", response_model=List[PromptResponse])
def list_items(
    skip: int = 0,
    limit: int = 100,
    search: str = Query("", description="Busca"),
    category: str = Query("", description="Categoria"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_prompts(db, skip=skip, limit=limit, search=search, category=category)


@router.post("", response_model=PromptResponse, status_code=201)
def create_item(
    item: PromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    return crud.create_prompt(db, item)

@router.get("/{item_id}", response_model=PromptResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = crud.get_prompt(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    return obj

@router.put("/{item_id}", response_model=PromptResponse)
def update_item(
    item_id: int,
    item: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    obj = crud.update_prompt(db, item_id, item)
    if not obj:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    return obj

@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
):
    obj = crud.delete_prompt(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Prompt não encontrado")
    return None

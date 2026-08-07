from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from schemas import DashboardStats, ActivityCreate, ActivityResponse
from auth.dependencies import get_current_user
from models import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_dashboard_stats(db)


@router.get("/activities", response_model=List[ActivityResponse])
def list_activities(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_activities(db, skip=skip, limit=limit)


@router.post("/activities", response_model=ActivityResponse, status_code=201)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_activity(db, activity)

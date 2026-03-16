from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Group
)
from app.schemas.group import GroupRead

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)


@router.get("/", response_model=list[GroupRead])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    statement = (
        select(Group).order_by(Group.created_at.desc()).offset(skip).limit(limit)
    )
    groups = db.execute(statement).scalars().all()
    return groups
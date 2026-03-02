from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    User
)
from app.schemas.user import UserRead

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/", response_model=list[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    statement = (
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    users = db.execute(statement).scalars().all()
    return users
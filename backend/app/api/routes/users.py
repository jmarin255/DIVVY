from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    User
)
from app.schemas.user import UserRead, UserCreate
from app.core.security import get_password_hash
from fastapi import HTTPException

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

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.execute(select(User).where(User.email == user.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone number already exists (if provided)
    if user.phone:
        existing_phone = db.execute(select(User).where(User.phone == user.phone)).scalar_one_or_none()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create new user
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        password_hash=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
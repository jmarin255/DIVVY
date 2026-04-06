from app.core.config import settings
from app.core.security import (
    get_current_user,
    get_password_hash,
    require_dev,
)
from app.db.session import get_db
from app.models import (
    User,
)
from app.schemas.user import UserCreate, UserRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_dev),
):
    """List users for developer accounts only.

    Validation:
    - `skip` and `limit` query params are optional pagination controls.
    - Caller must be a developer email from `DEV_EMAILS`.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - Does not use cookie-based auth for this endpoint.
    - No token in request body.
    """
    statement = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    users = db.execute(statement).scalars().all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_dev),
):
    """Get a single user by id for developer accounts only.

    Validation:
    - Caller must be a developer email from `DEV_EMAILS`.
    - `user_id` must exist or returns 404.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - Does not use cookie-based auth for this endpoint.
    - No token in request body.
    """
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account.

    Validation:
    - Requires JSON body matching `UserCreate`.
    - Email must be unique.
    - Phone must be unique when provided.

    Auth input:
    - No bearer token required.
    - No cookie required.
    - No token in request body.
    """
    # Check if email already exists
    existing_user = db.execute(
        select(User).where(User.email == user.email)
    ).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone number already exists (if provided)
    if user.phone:
        existing_phone = db.execute(
            select(User).where(User.phone == user.phone)
        ).scalar_one_or_none()
        if existing_phone:
            raise HTTPException(
                status_code=400, detail="Phone number already registered"
            )

    # Create new user
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        password_hash=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a user account by id.

    Validation:
    - Allowed when caller is deleting self, or caller email is in `DEV_EMAILS`.
    - `user_id` must exist or returns 404.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    current_user_id = int(getattr(current_user, "id"))
    current_user_email = str(getattr(current_user, "email", "")).lower()
    is_dev = current_user_email in settings.DEV_EMAILS

    if current_user_id != user_id and not is_dev:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account unless you are a developer",
        )

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


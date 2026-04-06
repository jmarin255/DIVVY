from app.core.security import get_current_user
from app.db.session import get_db
from app.models import (
    GroupMembership,
    User,
)
from app.schemas.group import GroupWithMembership
from app.schemas.user import UserRead
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/", response_model=UserRead)
def read_my_profile(current_user: User = Depends(get_current_user)):
    """Return profile for the currently authenticated user.

    Validation:
    - Access token must map to an existing user.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    return current_user


@router.get("/groups", response_model=list[GroupWithMembership])
def read_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return groups where the current user has membership.

    Validation:
    - Access token must map to an existing user.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    memberships = (
        db.execute(
            select(GroupMembership).where(
                GroupMembership.user_id == int(getattr(current_user, "id"))
            )
        )
        .scalars()
        .all()
    )

    return [
        GroupWithMembership(
            id=int(getattr(membership.group, "id")),
            name=str(getattr(membership.group, "name")),
            join_code=str(getattr(membership.group, "join_code")),
            created_at=getattr(membership.group, "created_at"),
            role=str(getattr(membership, "role")),
            joined_at=getattr(membership, "joined_at"),
        )
        for membership in memberships
    ]


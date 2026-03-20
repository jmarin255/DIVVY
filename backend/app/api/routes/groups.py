from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import (
    Group,
    GroupMembership,
    User
)
from app.schemas.group import GroupCreate, GroupRead
from app.schemas.user import UserRead
from app.api.routes.auth import get_current_user

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)


def is_dev_user(current_user: User) -> bool:
    current_user_email = str(getattr(current_user, "email", "")).lower()
    return current_user_email in settings.dev_emails


def require_dev(current_user: User = Depends(get_current_user)) -> User:
    if not is_dev_user(current_user):
        raise HTTPException(status_code=403, detail="Developer access required")
    return current_user


def is_group_owner(db: Session, group_id: int, current_user_id: int) -> bool:
    owner_membership = db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user_id,
            GroupMembership.role == "owner",
        )
    ).scalar_one_or_none()
    return owner_membership is not None


def ensure_group_member_write_access(
    db: Session,
    group_id: int,
    target_user_id: int,
    current_user: User,
) -> None:
    current_user_id = int(getattr(current_user, "id"))
    if target_user_id == current_user_id:
        return
    if is_dev_user(current_user):
        return
    if is_group_owner(db, group_id, current_user_id):
        return

    raise HTTPException(
        status_code=403,
        detail="You can only manage yourself unless you are the group owner or a developer",
    )


@router.get("/", response_model=list[GroupRead])
def read_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_dev),
):
    """List groups for developer accounts only.

    Validation:
    - `skip` and `limit` query params are optional pagination controls.
    - Caller must be a developer email from `DEV_EMAILS`.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    statement = (
        select(Group).order_by(Group.created_at.desc()).offset(skip).limit(limit)
    )
    groups = db.execute(statement).scalars().all()
    return groups

@router.get("/{group_id}", response_model=GroupRead)
def read_group(group_id: int, db: Session = Depends(get_db)):
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/{group_id}/users", response_model=list[UserRead])
def read_group_users(
    group_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_dev),
):
    """List users in a group for developer accounts only.

    Validation:
    - `group_id` must exist or returns 404.
    - Caller must be a developer email from `DEV_EMAILS`.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return [membership.user for membership in group.memberships]

@router.post("/", response_model=GroupRead)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a group and assign the authenticated creator as owner.

    Validation:
    - Requires JSON body matching `GroupCreate` (group `name`).
    - Caller must be an authenticated user.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    new_group = Group(name=group.name)
    db.add(new_group)

    db.flush()

    owner_membership = GroupMembership(
        user_id=int(getattr(current_user, "id")),
        group_id=int(getattr(new_group, "id")),
        role="owner",
    )
    db.add(owner_membership)

    db.commit()
    db.refresh(new_group)
    return new_group

@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a group.

    Validation:
    - `group_id` must exist or returns 404.
    - Caller must be group owner or developer (`DEV_EMAILS`).

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    current_user_id = int(getattr(current_user, "id"))
    if not is_dev_user(current_user) and not is_group_owner(db, group_id, current_user_id):
        raise HTTPException(status_code=403, detail="Only the group owner or a developer can delete this group")

    db.delete(group)
    db.commit()
    return {"message": "Group deleted successfully"}

@router.post("/{group_id}/users/{user_id}")
def add_user_to_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a user to a group.

    Validation:
    - `group_id` and `user_id` must exist.
    - Target user must not already be in the group.
    - Caller must be self-targeting, group owner, or developer.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    ensure_group_member_write_access(db, group_id, user_id, current_user)
    
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a member of the group
    existing_membership = db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of the group")
    
    new_membership = GroupMembership(user_id=user_id, group_id=group_id, role="member")
    db.add(new_membership)
    db.commit()
    return {"message": f"User {user.first_name} added to group: {group.name} successfully"}

@router.delete("/{group_id}/users/{user_id}")
def remove_user_from_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a user from a group.

    Validation:
    - `group_id` must exist.
    - Membership for `group_id/user_id` must exist.
    - Caller must be self-targeting, group owner, or developer.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    ensure_group_member_write_access(db, group_id, user_id, current_user)

    membership = db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    db.delete(membership)
    db.commit()
    return {"message": f"User removed from group successfully"}
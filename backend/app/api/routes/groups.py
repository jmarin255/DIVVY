from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Group,
    GroupMembership,
    User
)
from app.schemas.group import GroupRead
from app.schemas.user import UserRead

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

@router.get("/{group_id}", response_model=GroupRead)
def read_group(group_id: int, db: Session = Depends(get_db)):
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/{group_id}/users", response_model=list[UserRead])
def read_group_users(group_id: int, db: Session = Depends(get_db)):
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return [membership.user for membership in group.memberships]

@router.post("/", response_model=GroupRead)
def create_group(group: GroupRead, db: Session = Depends(get_db)):
    new_group = Group(name=group.name)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"message": "Group deleted successfully"}

@router.post("/{group_id}/users/{user_id}")
def add_user_to_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
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
def remove_user_from_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
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
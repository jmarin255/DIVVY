from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Group
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

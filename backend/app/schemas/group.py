from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GroupWithMembership(GroupRead):
    role: str
    joined_at: datetime | None = None

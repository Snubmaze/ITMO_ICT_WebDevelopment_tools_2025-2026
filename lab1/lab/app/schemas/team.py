import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserShort


class TeamCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None


class MemberAdd(BaseModel):
    user_id: uuid.UUID
    role: str = Field(default="member", pattern="^(leader|member|observer)$")


class MemberResponse(BaseModel):
    user: UserShort
    role: str

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: Optional[str]
    members: list[MemberResponse] = []

    model_config = {"from_attributes": True}

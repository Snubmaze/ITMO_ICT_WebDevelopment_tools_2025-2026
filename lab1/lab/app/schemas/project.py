import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="open", pattern="^(open|in_progress|closed)$")
    deadline: Optional[date] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(open|in_progress|closed)$")
    deadline: Optional[date] = None


class TeamShort(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class SkillShort(BaseModel):
    id: uuid.UUID
    skill_id: uuid.UUID

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    deadline: Optional[date]
    created_at: datetime
    teams: list[TeamShort] = []
    skill_links: list[SkillShort] = []

    model_config = {"from_attributes": True}

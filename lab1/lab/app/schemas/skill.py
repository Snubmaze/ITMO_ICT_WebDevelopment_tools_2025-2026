import uuid

from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class SkillWithLevel(BaseModel):
    id: uuid.UUID
    name: str
    level: str

    model_config = {"from_attributes": True}

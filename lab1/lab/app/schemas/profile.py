import uuid
from typing import Optional, Any, List

from pydantic import BaseModel, Field, model_validator

from app.schemas.skill import SkillWithLevel
from app.schemas.user import UserShort


class ProfileCreate(BaseModel):
    bio: Optional[str] = None
    experience: int = Field(default=0, ge=0)
    city: Optional[str] = Field(default=None, max_length=100)
    github_url: Optional[str] = Field(default=None, max_length=500)


class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0)
    city: Optional[str] = Field(default=None, max_length=100)
    github_url: Optional[str] = Field(default=None, max_length=500)


class ProfileSkillAdd(BaseModel):
    skill_id: uuid.UUID
    level: str = Field(default="beginner", pattern="^(beginner|mid|expert)$")


class ProfileResponse(BaseModel):
    id: uuid.UUID
    user: UserShort
    bio: Optional[str]
    experience: int
    city: Optional[str]
    github_url: Optional[str]
    skills: List[SkillWithLevel] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_skills(cls, data: Any) -> Any:
        if hasattr(data, "skill_links"):
            skills = [
                SkillWithLevel(id=link.skill.id, name=link.skill.name, level=link.level)
                for link in (data.skill_links or [])
            ]
            return {
                "id": data.id,
                "user": data.user,
                "bio": data.bio,
                "experience": data.experience,
                "city": data.city,
                "github_url": data.github_url,
                "skills": skills,
            }
        return data

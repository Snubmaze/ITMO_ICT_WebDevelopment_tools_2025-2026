import uuid
from typing import Optional, List

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")
    skill_links: Mapped[List["ProfileSkill"]] = relationship(
        "ProfileSkill", back_populates="profile", cascade="all, delete-orphan"
    )


class ProfileSkill(Base):
    __tablename__ = "profile_skills"

    profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")

    profile: Mapped["Profile"] = relationship("Profile", back_populates="skill_links")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="profile_links")

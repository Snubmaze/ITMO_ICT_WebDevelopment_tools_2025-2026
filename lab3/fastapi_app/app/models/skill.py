import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    profile_links: Mapped[list["ProfileSkill"]] = relationship("ProfileSkill", back_populates="skill")
    project_links: Mapped[list["ProjectSkill"]] = relationship("ProjectSkill", back_populates="skill")

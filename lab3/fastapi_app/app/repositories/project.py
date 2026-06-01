import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectSkill


def _with_relations():
    return [selectinload(Project.teams), selectinload(Project.skill_links)]


async def get_by_id(session: AsyncSession, project_id: uuid.UUID) -> Optional[Project]:
    result = await session.execute(
        select(Project).where(Project.id == project_id).options(*_with_relations())
    )
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    status: Optional[str] = None,
    skill_id: Optional[uuid.UUID] = None,
) -> list[Project]:
    query = select(Project).options(*_with_relations())
    if status:
        query = query.where(Project.status == status)
    if skill_id:
        query = query.where(
            Project.id.in_(
                select(ProjectSkill.project_id).where(ProjectSkill.skill_id == skill_id)
            )
        )
    result = await session.execute(query)
    return list(result.scalars().all())


async def create(session: AsyncSession, owner_id: uuid.UUID, data: dict) -> Project:
    project = Project(owner_id=owner_id, **data)
    session.add(project)
    await session.commit()
    result = await session.execute(
        select(Project).where(Project.id == project.id).options(*_with_relations())
    )
    return result.scalar_one()


async def update(session: AsyncSession, project: Project, data: dict) -> Project:
    for key, value in data.items():
        if value is not None:
            setattr(project, key, value)
    await session.commit()
    result = await session.execute(
        select(Project).where(Project.id == project.id).options(*_with_relations())
    )
    return result.scalar_one()


async def delete(session: AsyncSession, project: Project) -> None:
    await session.delete(project)
    await session.commit()

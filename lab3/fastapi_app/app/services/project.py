import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.repositories import project as project_repo
from app.models.project import Project


async def create(session: AsyncSession, owner_id: uuid.UUID, data: dict) -> Project:
    return await project_repo.create(session, owner_id, data)


async def get_all(
    session: AsyncSession,
    status: Optional[str] = None,
    skill_id: Optional[uuid.UUID] = None,
) -> list[Project]:
    return await project_repo.get_all(session, status, skill_id)


async def get_by_id(session: AsyncSession, project_id: uuid.UUID) -> Project:
    project = await project_repo.get_by_id(session, project_id)
    if not project:
        raise NotFoundError("Проект не найден")
    return project


async def update(session: AsyncSession, project_id: uuid.UUID, owner_id: uuid.UUID, data: dict) -> Project:
    project = await project_repo.get_by_id(session, project_id)
    if not project:
        raise NotFoundError("Проект не найден")
    if project.owner_id != owner_id:
        raise PermissionDeniedError("Только владелец может редактировать проект")
    return await project_repo.update(session, project, data)


async def delete(session: AsyncSession, project_id: uuid.UUID, owner_id: uuid.UUID) -> None:
    project = await project_repo.get_by_id(session, project_id)
    if not project:
        raise NotFoundError("Проект не найден")
    if project.owner_id != owner_id:
        raise PermissionDeniedError("Только владелец может удалить проект")
    await project_repo.delete(session, project)

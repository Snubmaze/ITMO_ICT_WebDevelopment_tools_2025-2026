import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories import team as team_repo
from app.repositories import project as project_repo
from app.repositories import user as user_repo
from app.models.team import Team


async def create(session: AsyncSession, data: dict) -> Team:
    project = await project_repo.get_by_id(session, data["project_id"])
    if not project:
        raise NotFoundError("Проект не найден")
    return await team_repo.create(session, data)


async def get_by_id(session: AsyncSession, team_id: uuid.UUID) -> Team:
    team = await team_repo.get_by_id(session, team_id)
    if not team:
        raise NotFoundError("Команда не найдена")
    return team


async def update(session: AsyncSession, team_id: uuid.UUID, data: dict) -> Team:
    team = await team_repo.get_by_id(session, team_id)
    if not team:
        raise NotFoundError("Команда не найдена")
    return await team_repo.update(session, team, data)


async def delete(session: AsyncSession, team_id: uuid.UUID) -> None:
    team = await team_repo.get_by_id(session, team_id)
    if not team:
        raise NotFoundError("Команда не найдена")
    await team_repo.delete(session, team)


async def add_member(session: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID, role: str) -> Team:
    team = await team_repo.get_by_id(session, team_id)
    if not team:
        raise NotFoundError("Команда не найдена")
    user = await user_repo.get_by_id(session, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    return await team_repo.add_member(session, team, user_id, role)


async def remove_member(session: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID) -> Team:
    team = await team_repo.get_by_id(session, team_id)
    if not team:
        raise NotFoundError("Команда не найдена")
    return await team_repo.remove_member(session, team, user_id)

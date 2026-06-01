import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, AlreadyExistsError
from app.repositories import skill as skill_repo
from app.models.skill import Skill


async def create(session: AsyncSession, name: str) -> Skill:
    if await skill_repo.get_by_name(session, name):
        raise AlreadyExistsError(f"Навык '{name}' уже существует")
    return await skill_repo.create(session, name)


async def get_all(session: AsyncSession) -> list[Skill]:
    return await skill_repo.get_all(session)


async def get_by_id(session: AsyncSession, skill_id: uuid.UUID) -> Skill:
    skill = await skill_repo.get_by_id(session, skill_id)
    if not skill:
        raise NotFoundError("Навык не найден")
    return skill


async def delete(session: AsyncSession, skill_id: uuid.UUID) -> None:
    skill = await skill_repo.get_by_id(session, skill_id)
    if not skill:
        raise NotFoundError("Навык не найден")
    await skill_repo.delete(session, skill)

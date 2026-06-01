import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, AlreadyExistsError
from app.repositories import profile as profile_repo
from app.repositories import skill as skill_repo
from app.models.profile import Profile


async def create(session: AsyncSession, user_id: uuid.UUID, data: dict) -> Profile:
    if await profile_repo.get_by_user_id(session, user_id):
        raise AlreadyExistsError("Профиль уже существует")
    return await profile_repo.create(session, user_id, data)


async def get_all(session: AsyncSession, skill_id: Optional[uuid.UUID] = None) -> list[Profile]:
    return await profile_repo.get_all(session, skill_id)


async def get_by_id(session: AsyncSession, profile_id: uuid.UUID) -> Profile:
    profile = await profile_repo.get_by_id(session, profile_id)
    if not profile:
        raise NotFoundError("Профиль не найден")
    return profile


async def update(session: AsyncSession, profile_id: uuid.UUID, data: dict) -> Profile:
    profile = await profile_repo.get_by_id(session, profile_id)
    if not profile:
        raise NotFoundError("Профиль не найден")
    return await profile_repo.update(session, profile, data)


async def delete(session: AsyncSession, profile_id: uuid.UUID) -> None:
    profile = await profile_repo.get_by_id(session, profile_id)
    if not profile:
        raise NotFoundError("Профиль не найден")
    await profile_repo.delete(session, profile)


async def add_skill(session: AsyncSession, profile_id: uuid.UUID, skill_id: uuid.UUID, level: str) -> Profile:
    profile = await profile_repo.get_by_id(session, profile_id)
    if not profile:
        raise NotFoundError("Профиль не найден")
    skill = await skill_repo.get_by_id(session, skill_id)
    if not skill:
        raise NotFoundError("Навык не найден")
    return await profile_repo.add_skill(session, profile, skill_id, level)


async def remove_skill(session: AsyncSession, profile_id: uuid.UUID, skill_id: uuid.UUID) -> Profile:
    profile = await profile_repo.get_by_id(session, profile_id)
    if not profile:
        raise NotFoundError("Профиль не найден")
    return await profile_repo.remove_skill(session, profile, skill_id)

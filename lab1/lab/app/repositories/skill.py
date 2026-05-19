import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


async def get_by_id(session: AsyncSession, skill_id: uuid.UUID) -> Optional[Skill]:
    result = await session.execute(select(Skill).where(Skill.id == skill_id))
    return result.scalar_one_or_none()


async def get_by_name(session: AsyncSession, name: str) -> Optional[Skill]:
    result = await session.execute(select(Skill).where(Skill.name == name))
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession) -> list[Skill]:
    result = await session.execute(select(Skill))
    return list(result.scalars().all())


async def create(session: AsyncSession, name: str) -> Skill:
    skill = Skill(name=name)
    session.add(skill)
    await session.commit()
    await session.refresh(skill)
    return skill


async def delete(session: AsyncSession, skill: Skill) -> None:
    await session.delete(skill)
    await session.commit()

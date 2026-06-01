import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import Profile, ProfileSkill


def _with_relations():
    return [
        selectinload(Profile.skill_links).selectinload(ProfileSkill.skill),
        selectinload(Profile.user),
    ]


async def get_by_id(session: AsyncSession, profile_id: uuid.UUID) -> Optional[Profile]:
    result = await session.execute(
        select(Profile).where(Profile.id == profile_id).options(*_with_relations())
    )
    return result.scalar_one_or_none()


async def get_by_user_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[Profile]:
    result = await session.execute(
        select(Profile).where(Profile.user_id == user_id).options(*_with_relations())
    )
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession, skill_id: Optional[uuid.UUID] = None) -> list[Profile]:
    query = select(Profile).options(*_with_relations())
    if skill_id:
        query = query.join(Profile.skill_links).where(ProfileSkill.skill_id == skill_id)
    result = await session.execute(query)
    return list(result.scalars().unique().all())


async def create(session: AsyncSession, user_id: uuid.UUID, data: dict) -> Profile:
    profile = Profile(user_id=user_id, **data)
    session.add(profile)
    await session.commit()
    result = await session.execute(
        select(Profile).where(Profile.id == profile.id).options(*_with_relations())
    )
    return result.scalar_one()


async def update(session: AsyncSession, profile: Profile, data: dict) -> Profile:
    for key, value in data.items():
        if value is not None:
            setattr(profile, key, value)
    await session.commit()
    await session.refresh(profile)
    result = await session.execute(
        select(Profile).where(Profile.id == profile.id).options(*_with_relations())
    )
    return result.scalar_one()


async def delete(session: AsyncSession, profile: Profile) -> None:
    await session.delete(profile)
    await session.commit()


async def add_skill(session: AsyncSession, profile: Profile, skill_id: uuid.UUID, level: str) -> Profile:
    profile_id = profile.id
    existing = await session.execute(
        select(ProfileSkill).where(
            ProfileSkill.profile_id == profile_id,
            ProfileSkill.skill_id == skill_id,
        )
    )
    link = existing.scalar_one_or_none()
    if link:
        link.level = level
    else:
        link = ProfileSkill(profile_id=profile_id, skill_id=skill_id, level=level)
        session.add(link)
    await session.commit()
    session.expire_all()
    result = await session.execute(
        select(Profile).where(Profile.id == profile_id).options(*_with_relations())
    )
    return result.scalar_one()


async def remove_skill(session: AsyncSession, profile: Profile, skill_id: uuid.UUID) -> Profile:
    profile_id = profile.id
    result = await session.execute(
        select(ProfileSkill).where(
            ProfileSkill.profile_id == profile_id,
            ProfileSkill.skill_id == skill_id,
        )
    )
    link = result.scalar_one_or_none()
    if link:
        await session.delete(link)
        await session.commit()
    session.expire_all()
    result = await session.execute(
        select(Profile).where(Profile.id == profile_id).options(*_with_relations())
    )
    return result.scalar_one()

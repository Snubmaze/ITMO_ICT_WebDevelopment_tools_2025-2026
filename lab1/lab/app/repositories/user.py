import uuid
from typing import Optional, Union, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_id(session: AsyncSession, user_id: Union[str, uuid.UUID]) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession) -> List[User]:
    result = await session.execute(select(User))
    return list(result.scalars().all())


async def create_user(session: AsyncSession, data: dict) -> User:
    user = User(**data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user_id: Union[str, uuid.UUID], data: dict) -> Optional[User]:
    user = await get_by_id(session, user_id)
    if not user:
        return None
    for key, value in data.items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import Team, TeamMember


def _with_relations():
    return [selectinload(Team.members).selectinload(TeamMember.user)]


async def get_by_id(session: AsyncSession, team_id: uuid.UUID) -> Optional[Team]:
    result = await session.execute(
        select(Team).where(Team.id == team_id).options(*_with_relations())
    )
    return result.scalar_one_or_none()


async def create(session: AsyncSession, data: dict) -> Team:
    team = Team(**data)
    session.add(team)
    await session.commit()
    result = await session.execute(
        select(Team).where(Team.id == team.id).options(*_with_relations())
    )
    return result.scalar_one()


async def update(session: AsyncSession, team: Team, data: dict) -> Team:
    for key, value in data.items():
        if value is not None:
            setattr(team, key, value)
    await session.commit()
    result = await session.execute(
        select(Team).where(Team.id == team.id).options(*_with_relations())
    )
    return result.scalar_one()


async def delete(session: AsyncSession, team: Team) -> None:
    await session.delete(team)
    await session.commit()


async def add_member(session: AsyncSession, team: Team, user_id: uuid.UUID, role: str) -> Team:
    team_id = team.id
    existing = await session.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    )
    member = existing.scalar_one_or_none()
    if member:
        member.role = role
    else:
        member = TeamMember(team_id=team_id, user_id=user_id, role=role)
        session.add(member)
    await session.commit()
    session.expire_all()
    result = await session.execute(
        select(Team).where(Team.id == team_id).options(*_with_relations())
    )
    return result.scalar_one()


async def remove_member(session: AsyncSession, team: Team, user_id: uuid.UUID) -> Team:
    team_id = team.id
    result = await session.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if member:
        await session.delete(member)
        await session.commit()
    session.expire_all()
    result = await session.execute(
        select(Team).where(Team.id == team_id).options(*_with_relations())
    )
    return result.scalar_one()

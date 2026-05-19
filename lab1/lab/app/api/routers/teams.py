import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.services import team as team_service
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, MemberAdd

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamResponse, status_code=201)
async def create_team(
    data: TeamCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> TeamResponse:
    return await team_service.create(session, data.model_dump())


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> TeamResponse:
    return await team_service.get_by_id(session, team_id)


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: uuid.UUID,
    data: TeamUpdate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> TeamResponse:
    return await team_service.update(session, team_id, data.model_dump(exclude_unset=True))


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    await team_service.delete(session, team_id)


@router.post("/{team_id}/members", response_model=TeamResponse)
async def add_member(
    team_id: uuid.UUID,
    data: MemberAdd,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> TeamResponse:
    return await team_service.add_member(session, team_id, data.user_id, data.role)


@router.delete("/{team_id}/members/{user_id}", response_model=TeamResponse)
async def remove_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> TeamResponse:
    return await team_service.remove_member(session, team_id, user_id)

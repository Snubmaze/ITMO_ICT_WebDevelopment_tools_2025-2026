import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.services import profile as profile_service
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, ProfileSkillAdd

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileResponse, status_code=201)
async def create_profile(
    data: ProfileCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ProfileResponse:
    return await profile_service.create(session, user.id, data.model_dump())


@router.get("", response_model=list[ProfileResponse])
async def list_profiles(
    skill_id: Optional[uuid.UUID] = Query(default=None),
    session: AsyncSession = Depends(get_db),
) -> list[ProfileResponse]:
    return await profile_service.get_all(session, skill_id)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> ProfileResponse:
    return await profile_service.get_by_id(session, profile_id)


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: uuid.UUID,
    data: ProfileUpdate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ProfileResponse:
    return await profile_service.update(session, profile_id, data.model_dump(exclude_unset=True))


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    await profile_service.delete(session, profile_id)


@router.post("/{profile_id}/skills", response_model=ProfileResponse)
async def add_skill_to_profile(
    profile_id: uuid.UUID,
    data: ProfileSkillAdd,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ProfileResponse:
    return await profile_service.add_skill(session, profile_id, data.skill_id, data.level)


@router.delete("/{profile_id}/skills/{skill_id}", response_model=ProfileResponse)
async def remove_skill_from_profile(
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ProfileResponse:
    return await profile_service.remove_skill(session, profile_id, skill_id)

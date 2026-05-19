import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.services import skill as skill_service
from app.schemas.skill import SkillCreate, SkillResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("", response_model=SkillResponse, status_code=201)
async def create_skill(
    data: SkillCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> SkillResponse:
    return await skill_service.create(session, data.name)


@router.get("", response_model=list[SkillResponse])
async def list_skills(session: AsyncSession = Depends(get_db)) -> list[SkillResponse]:
    return await skill_service.get_all(session)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> SkillResponse:
    return await skill_service.get_by_id(session, skill_id)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(
    skill_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    await skill_service.delete(session, skill_id)

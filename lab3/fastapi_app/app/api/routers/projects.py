import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.services import project as project_service
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ProjectResponse:
    return await project_service.create(session, user.id, data.model_dump())


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    status: Optional[str] = Query(default=None),
    skill_id: Optional[uuid.UUID] = Query(default=None),
    session: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    return await project_service.get_all(session, status, skill_id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> ProjectResponse:
    return await project_service.get_by_id(session, project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> ProjectResponse:
    return await project_service.update(session, project_id, user.id, data.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> None:
    await project_service.delete(session, project_id, user.id)

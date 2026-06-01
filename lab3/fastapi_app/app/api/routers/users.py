from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.repositories import user as user_repo
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)) -> UserResponse:
    return user


@router.get("", response_model=list[UserResponse])
async def list_users(session: AsyncSession = Depends(get_db)) -> list[UserResponse]:
    return await user_repo.get_all(session)

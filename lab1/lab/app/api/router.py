from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.api.routers.profiles import router as profiles_router
from app.api.routers.skills import router as skills_router
from app.api.routers.projects import router as projects_router
from app.api.routers.teams import router as teams_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(profiles_router)
router.include_router(skills_router)
router.include_router(projects_router)
router.include_router(teams_router)

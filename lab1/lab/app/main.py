from fastapi import FastAPI

from app.config import settings
from app.api.router import router
from app.core.exceptions import AppError
from app.core.error_handlers import app_error_handler


app = FastAPI(
    title=settings.APP_TITLE,
    description="API платформы для поиска людей в команду",
)


app.include_router(router, prefix="/api")
app.add_exception_handler(AppError, app_error_handler)

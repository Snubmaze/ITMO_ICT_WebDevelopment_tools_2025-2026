from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, TokenType, decrypt_token
from app.core.exceptions import AuthError, PermissionDeniedError
from app.repositories.token import is_blacklisted
from app.repositories import user as user_repo
from app.database import get_db  # noqa: F401 — re-exported for routers
from app.config import settings


async def get_current_user(request: Request, session: AsyncSession = Depends(get_db)) -> dict:
    encrypted_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if not encrypted_token:
        raise AuthError("Не авторизован")
    
    token = decrypt_token(encrypted_token)
    if await is_blacklisted(token):
        raise AuthError("Токен отозван")

    payload = decode_token(token, TokenType.ACCESS)
    if not payload:
        raise AuthError("Невалидный токен")

    user = await user_repo.get_by_id(session, payload["sub"])
    if not user:
        raise AuthError("Пользователь не найден")

    return user


def require_role(role: str):
    async def checker(user=Depends(get_current_user)):
        if user.role != role:
            raise PermissionDeniedError("Недостаточно прав")
        return user
    return checker
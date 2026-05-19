from fastapi import APIRouter, Request, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_token, decrypt_token
from app.core.exceptions import AuthError
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest 
from app.services import auth as auth_service
from app.api.deps import get_current_user, get_db
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_token_cookies(response: Response, tokens: dict) -> None:
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=encrypt_token(tokens["access_token"]),
        max_age=settings.COOKIE_MAX_AGE_ACCESS,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=encrypt_token(tokens["refresh_token"]),
        max_age=settings.COOKIE_MAX_AGE_REFRESH,
        httponly=True,
        secure=True,
        samesite="lax",
    )


def _delete_token_cookies(response: Response) -> None:
    response.delete_cookie(settings.ACCESS_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME)


@router.post("/register")
async def register(data: RegisterRequest, response: Response, session: AsyncSession = Depends(get_db)):
    tokens = await auth_service.register(
        session=session,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        role=data.role,
    )
    _set_token_cookies(response, tokens)
    return {"detail": "Регистрация успешна"}


@router.post("/login")
async def login(data: LoginRequest, response: Response, session: AsyncSession = Depends(get_db)):
    tokens = await auth_service.login(
        session=session,
        email=data.email,
        password=data.password,
    )
    _set_token_cookies(response, tokens)
    return {"detail": "Вход выполнен"}


@router.post("/refresh")
async def refresh(request: Request, response: Response, session: AsyncSession = Depends(get_db)):
    encrypted_refresh = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not encrypted_refresh:
        raise AuthError("Refresh токен отсутствует")

    refresh_token = decrypt_token(encrypted_refresh)

    tokens = await auth_service.refresh(session, refresh_token)
    _set_token_cookies(response, tokens)
    return {"detail": "Токены обновлены"}


@router.post("/logout")
async def logout(request: Request, response: Response, user=Depends(get_current_user)):
    encrypted_access = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if not encrypted_access:
        raise AuthError("Не авторизован")
    
    encrypted_refresh = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not encrypted_refresh:
        raise AuthError("Отсутствует refresh токен")
    
    access_token = decrypt_token(encrypted_access)
    refresh_token = decrypt_token(encrypted_refresh)

    await auth_service.logout(access_token, refresh_token)
    _delete_token_cookies(response)
    return {"detail": "Выход выполнен"}


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await auth_service.change_password(session, user.id, data.old_password, data.new_password)
    return {"detail": "Пароль изменён"}

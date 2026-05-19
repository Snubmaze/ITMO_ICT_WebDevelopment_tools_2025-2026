import secrets
from datetime import datetime, timedelta, timezone

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    TokenType,
    hash_password,
    verify_password,
    create_token_pair,
    decode_token,
)
from app.core.exceptions import AuthError, AlreadyExistsError, NotFoundError, ValidationError
from app.repositories import user as user_repo
from app.repositories import token as token_repo
from app.config import settings


async def register(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    role: str = "employee",
) -> dict:
    if await user_repo.get_by_email(session, email):
        raise AlreadyExistsError("Аккаунт с указанной почтой уже существует")

    user = await user_repo.create_user(session, {
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "role": role,
    })

    return create_token_pair(str(user.id), user.role)


async def login(session: AsyncSession, email: str, password: str) -> dict:
    user = await user_repo.get_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Неверная почта или пароль")

    return create_token_pair(str(user.id), user.role)


async def refresh(session: AsyncSession, refresh_token: str) -> dict:
    if await token_repo.is_blacklisted(refresh_token):
        raise AuthError("Токен отозван")

    payload = decode_token(refresh_token, TokenType.REFRESH)
    if not payload:
        raise AuthError("Невалидный refresh токен")

    user_id = payload["sub"]
    user = await user_repo.get_by_id(session, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")

    await token_repo.add_to_blacklist(refresh_token)
    return create_token_pair(str(user.id), user.role)


async def logout(access_token: str, refresh_token: Optional[str] = None) -> None:
    await token_repo.add_to_blacklist(access_token)
    if refresh_token:
        await token_repo.add_to_blacklist(refresh_token)


async def change_password(session: AsyncSession, user_id: str, old_password: str, new_password: str) -> None:
    user = await user_repo.get_by_id(session, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")

    if not verify_password(old_password, user.password_hash):
        raise AuthError("Неверный текущий пароль")

    if old_password == new_password:
        raise ValidationError("Новый пароль не должен совпадать со старым")

    await user_repo.update_user(session, user_id, {
        "password_hash": hash_password(new_password),
    })


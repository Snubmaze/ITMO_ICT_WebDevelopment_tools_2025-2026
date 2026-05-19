from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
from enum import Enum
from cryptography.fernet import Fernet, InvalidToken

from app.config import settings 


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(settings.COOKIE_ENCRYPTION_KEY)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hash: str) -> bool:
    return pwd_context.verify(plain, hash)


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        data = {"sub": user_id, "role": role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS,
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        data = {"sub": user_id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type=TokenType.REFRESH
    )


def create_token_pair(user_id: str, role: str) -> dict[str, str]:
    return {
        "access_token": create_access_token(user_id, role),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer"
    }


def decode_token(token: str, expected_type: TokenType = TokenType.ACCESS) -> Optional[dict]:
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != expected_type.value:
            return None
        return payload
    except JWTError:
        return None


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    try:
        return fernet.decrypt(encrypted.encode()).decode()
    except InvalidToken:
        return None



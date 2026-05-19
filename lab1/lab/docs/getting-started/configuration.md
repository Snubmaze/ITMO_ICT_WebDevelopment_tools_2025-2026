# Конфигурация

Все настройки загружаются из файла `.env` в корне проекта через Pydantic `BaseSettings`.

## Переменные окружения

| Переменная | Обязательная | По умолчанию | Описание |
|---|---|---|---|
| `DATABASE_URL` | Да | — | Строка подключения к PostgreSQL async (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | Да | — | Секрет для подписи JWT |
| `ALGORITHM` | Нет | `HS256` | Алгоритм подписи JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Нет | `30` | Время жизни access-токена в минутах |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Нет | `7` | Время жизни refresh-токена в днях |
| `COOKIE_ENCRYPTION_KEY` | Да | — | Ключ Fernet для шифрования токенов перед сохранением в куки |
| `ACCESS_COOKIE_NAME` | Нет | `__sid` | Имя куки access-токена |
| `REFRESH_COOKIE_NAME` | Нет | `__rid` | Имя куки refresh-токена |
| `COOKIE_MAX_AGE_ACCESS` | Нет | `1800` | Максимальный возраст access-куки в секундах |
| `COOKIE_MAX_AGE_REFRESH` | Нет | `604800` | Максимальный возраст refresh-куки в секундах |

## Генерация ключей

**SECRET_KEY** — любая длинная случайная строка:

```bash
openssl rand -hex 32
```

**COOKIE_ENCRYPTION_KEY** — должен быть корректным ключом Fernet (URL-safe base64, 32 байта):

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Пример файла `.env`

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/teamfinder

SECRET_KEY=3d6f45a5fc12445dbac2f59c3b6c7cb1d16f0ec1d9f8e2a5b8c0fa3d7e9b2c4
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

COOKIE_ENCRYPTION_KEY=your-fernet-key-here
ACCESS_COOKIE_NAME=__sid
REFRESH_COOKIE_NAME=__rid
```

!!! warning
    Никогда не добавляйте `.env` в систему контроля версий. Добавьте его в `.gitignore`.

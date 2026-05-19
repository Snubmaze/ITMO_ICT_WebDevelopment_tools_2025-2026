# Установка и настройка

## Требования

- Python 3.9+
- PostgreSQL (запущенный и доступный)

## Шаги

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Создание файла `.env`

Создайте `.env` в корне проекта (рядом с `alembic.ini`):

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/teamfinder

SECRET_KEY=your-secret-key-here
COOKIE_ENCRYPTION_KEY=your-fernet-key-here
```

Для генерации ключа Fernet:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Все доступные переменные описаны в разделе [Конфигурация](configuration.md).

### 3. Запуск миграций базы данных

```bash
alembic upgrade head
```

### 4. Запуск сервера

```bash
uvicorn app.main:app --reload
```

API доступен по адресу `http://localhost:8000`.

| URL | Назначение |
|---|---|
| `http://localhost:8000/docs` | Swagger UI (интерактивный) |
| `http://localhost:8000/redoc` | Документация ReDoc |
| `http://localhost:8000/api/...` | Эндпоинты API |

## Структура проекта

```
app/
├── main.py               # FastAPI-приложение, регистрация роутеров, обработчики ошибок
├── config.py             # Настройки (загружаются из .env)
├── database.py           # Асинхронный движок SQLAlchemy и фабрика сессий
├── api/
│   ├── deps.py           # Внедрение зависимостей (аутентификация, сессия БД)
│   ├── router.py         # Корневой API-роутер
│   └── routers/          # По одному файлу на ресурс
├── core/
│   ├── exceptions.py     # Классы пользовательских исключений
│   ├── error_handlers.py # Маппинг исключений → HTTP-ответы
│   └── security.py       # Утилиты JWT, bcrypt, Fernet
├── models/               # ORM-модели SQLAlchemy
├── repositories/         # Асинхронные функции доступа к БД
├── schemas/              # Pydantic-модели запросов/ответов
└── services/             # Бизнес-логика
alembic/                  # Скрипты миграций
```

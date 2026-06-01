# Задача 1 — Упаковка приложения в Docker

**Цель:** упаковать FastAPI-приложение из lab1, парсер из lab2 и базу данных PostgreSQL в Docker-контейнеры и связать их через Docker Compose.

---

## Что такое Docker

Docker позволяет упаковать приложение вместе со всеми его зависимостями в изолированный **контейнер**. Контейнер запускается одинаково на любой машине — не нужно устанавливать Python нужной версии, PostgreSQL или системные библиотеки. Всё включено в образ.

| Понятие | Описание |
|---------|----------|
| **Image (образ)** | Шаблон контейнера. Описывается в `Dockerfile`. Собирается один раз, запускается многократно |
| **Container** | Запущенный экземпляр образа — это и есть работающее приложение |
| **Dockerfile** | Инструкция по сборке образа: базовый образ, зависимости, файлы, команда запуска |
| **docker-compose.yml** | Описание нескольких контейнеров сразу: образы, порты, зависимости, переменные |

---

## Dockerfile — синтаксис по строкам

Оба сервиса (`fastapi_app` и `parser_app`) используют одинаковую структуру Dockerfile:

```dockerfile
FROM python:3.11-slim
```
Берём официальный образ Python 3.11. Суффикс `-slim` — облегчённая версия без лишних утилит.

```dockerfile
WORKDIR /app
```
Все последующие команды выполняются в папке `/app` внутри контейнера. Если папки нет — Docker создаст её.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Сначала копируем только `requirements.txt` и устанавливаем зависимости. **Важная оптимизация**: Docker кэширует слои — если код изменился, но зависимости не менялись, слой с `pip install` возьмётся из кэша и пересобираться не будет.

```dockerfile
COPY . .
```
Копируем весь исходный код в `/app`.

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Команда при старте контейнера. `--host 0.0.0.0` обязателен — без него приложение слушает только `127.0.0.1` внутри контейнера и снаружи недоступно.

### Dockerfile для fastapi_app

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile для parser_app

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

!!! note "Разница в точке входа"
    `fastapi_app` использует `app.main:app` (вложенный пакет `app/`), а `parser_app` — `main:app` (плоская структура).

---

## Docker Compose — синтаксис по блокам

`docker-compose.yml` описывает все контейнеры системы и как они связаны.

### Сервис postgres

```yaml
postgres:
  image: postgres:16           # готовый образ с Docker Hub, сборка не нужна
  env_file: .env               # читает POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
  ports:
    - "5433:5432"              # хост:контейнер — снаружи :5433, внутри всегда :5432
  volumes:
    - postgres_data:/var/lib/postgresql/data   # данные переживают перезапуск
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
    interval: 5s
    retries: 5
```

`healthcheck` — Docker периодически запускает эту команду. Пока PostgreSQL не готов — сервис считается нездоровым, зависимые сервисы ждут.

### Сервис fastapi

```yaml
fastapi:
  build: ./fastapi_app         # собрать из Dockerfile в этой папке
  ports:
    - "8000:8000"
  env_file: .env               # переменные окружения из корневого .env
  depends_on:
    postgres:
      condition: service_healthy   # ждать пока postgres пройдёт healthcheck
    redis:
      condition: service_healthy
    parser:
      condition: service_started
```

`depends_on` с `condition: service_healthy` гарантирует, что FastAPI не запустится раньше базы данных.

### Управление переменными окружения

В проекте два механизма работы с переменными:

| Механизм | Где работает | Пример |
|----------|-------------|--------|
| `${VAR}` в yml | Подстановка при чтении файла docker-compose | `pg_isready -U ${POSTGRES_USER}` |
| `env_file: .env` | Передаёт переменные внутрь контейнера | `DATABASE_URL`, `SECRET_KEY` |

Все секреты хранятся в одном файле `lab3/.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=teamfinder

DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/teamfinder
SECRET_KEY=change-me-to-a-long-random-secret
...
```

!!! warning "localhost vs имя сервиса"
    Внутри Docker-сети `localhost` — это сам контейнер. Для обращения к другому контейнеру используется **имя сервиса** из `docker-compose.yml`. Поэтому `DATABASE_URL` содержит `@postgres:5432`, а не `@localhost:5432`.

!!! warning "Внешний и внутренний порт"
    Маппинг `5433:5432` означает: снаружи (хост-машина) порт `5433`, внутри Docker-сети всегда `5432`. `DATABASE_URL` всегда использует внутренний порт `:5432`.

---

## Полный docker-compose.yml

```yaml
services:

  postgres:
    image: postgres:16
    env_file: .env
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  parser:
    build: ./parser_app
    ports:
      - "8001:8001"

  fastapi:
    build: ./fastapi_app
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      parser:
        condition: service_started

  celery_worker:
    build: ./fastapi_app
    command: celery -A celery_app worker --loglevel=info
    env_file: .env
    depends_on:
      redis:
        condition: service_healthy
      parser:
        condition: service_started

volumes:
  postgres_data:
```

!!! tip "celery_worker и fastapi — один образ"
    `celery_worker` использует тот же `build: ./fastapi_app`, что и `fastapi`, но с другой командой запуска. Это стандартная практика: один образ — несколько точек входа.

---

## Запуск и миграции

```bash
# Собрать образы и запустить все контейнеры
docker compose up --build -d

# Проверить статус
docker compose ps

# Применить миграции Alembic (таблицы в PostgreSQL)
docker compose exec fastapi alembic upgrade head

# Посмотреть логи сервиса
docker compose logs fastapi --tail=30
```

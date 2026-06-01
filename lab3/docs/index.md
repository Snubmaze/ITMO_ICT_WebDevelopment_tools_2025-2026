# Лабораторная работа 3 — Docker, Парсер, Celery

## Цель работы

Научиться упаковывать FastAPI-приложение в Docker, интегрировать парсер данных как отдельный микросервис и организовать асинхронную обработку задач через очередь Celery + Redis.

## Итоговая архитектура

Система состоит из пяти Docker-контейнеров, запущенных через `docker-compose`:

```
Клиент (браузер / curl)
        │
        ▼
┌──────────────┐      HTTP      ┌──────────────┐
│   fastapi    │ ─────────────▶ │    parser    │
│  (lab1 API)  │                │  (lab2 код)  │
│   :8000      │                │   :8001      │
└──────┬───────┘                └──────────────┘
       │                               ▲
       │ SQL                           │ HTTP (через Celery)
       ▼                               │
┌──────────────┐      задачи    ┌──────────────┐
│  PostgreSQL  │    ┌────────▶  │celery_worker │
│   :5432      │    │           └──────────────┘
└──────────────┘    │
                    │ брокер
              ┌─────────────┐
              │    Redis    │
              │   :6379     │
              └─────────────┘
```

## Структура лабораторной работы

| Задача | Баллы | Описание |
|--------|-------|----------|
| [Задача 1](task1.md) | 70% | Упаковка FastAPI, PostgreSQL и парсера в Docker Compose |
| [Задача 2](task2.md) | 70% | Эндпоинт FastAPI для синхронного HTTP-вызова парсера |
| [Задача 3](task3.md) | 100% | Асинхронный вызов парсера через очередь Celery + Redis |

## Структура проекта

```
lab3/
├── docker-compose.yml       ← оркестрация всех сервисов
├── .env                     ← секреты (не коммитить в git)
├── fastapi_app/             ← lab1 + новые эндпоинты + Celery
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── celery_app.py
│   ├── tasks.py
│   └── app/
│       └── api/routers/parser.py
└── parser_app/              ← lab2 обёрнутый в FastAPI
    ├── Dockerfile
    ├── main.py
    └── parser.py
```

## Быстрый старт

```bash
# Запустить все сервисы
docker compose up --build -d

# Применить миграции БД (один раз)
docker compose exec fastapi alembic upgrade head

# Swagger-документация
open http://localhost:8000/docs
```

# Задача 3 — Celery + Redis: асинхронная очередь задач

**Цель:** вместо того чтобы ждать ответа парсера прямо в HTTP-запросе, поставить задачу в очередь и вернуть клиенту `task_id` немедленно.

---

## Зачем нужна очередь задач

Представь: пользователь отправляет URL на парсинг. Парсинг занимает 5–10 секунд. Если делать это синхронно:

```
Клиент ──POST──▶ FastAPI ──── ждёт 10 сек ────▶ ответ
                 (блокирован)
```

С Celery:

```
Клиент ──POST──▶ FastAPI ──▶ Redis (очередь) ──▶ {"task_id": "abc"}  (мгновенно)
                                   │
                                   ▼
                            Celery Worker ──▶ парсит ──▶ результат в Redis
                                   
Клиент ──GET /status/abc──▶ FastAPI ──▶ Redis ──▶ {"status": "success", "result": ...}
```

---

## Компоненты

### Redis

Redis здесь выполняет **две роли**:

| Роль | Назначение |
|------|-----------|
| **Broker** | Очередь задач. FastAPI кладёт задачу, Worker забирает |
| **Backend** | Хранилище результатов. Worker сохраняет результат, FastAPI читает по `task_id` |

```env
REDIS_URL=redis://redis:6379/0    # /0 — номер базы Redis (0..15)
```

### Celery Worker

Отдельный процесс (контейнер), который в бесконечном цикле:
1. Ждёт задачи в очереди Redis
2. Берёт задачу
3. Выполняет её
4. Сохраняет результат обратно в Redis

---

## Код

### celery_app.py — инициализация

```python
from celery import Celery
from app.config import settings

celery_app = Celery(
    "lab3",
    broker=settings.REDIS_URL,    # откуда брать задачи
    backend=settings.REDIS_URL,   # куда сохранять результаты
    include=["tasks"],            # файл tasks.py с задачами
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)
```

`include=["tasks"]` — при старте Worker импортирует `tasks.py` и регистрирует все задачи.

### tasks.py — определение задачи

```python
import httpx
from celery_app import celery_app
from app.config import settings

@celery_app.task(bind=True, name="parse_url_task")
def parse_url_task(self, url: str):
    try:
        with httpx.Client(timeout=30) as client:  # sync клиент — Celery не async
            response = client.post(
                f"{settings.PARSER_URL}/parse",
                json={"url": url},
            )
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5, max_retries=3)
```

Разбор декоратора:

| Параметр | Назначение |
|----------|-----------|
| `bind=True` | Передаёт `self` (объект задачи) — нужен для `self.retry()` |
| `name="parse_url_task"` | Уникальное имя задачи в очереди |
| `self.retry(countdown=5, max_retries=3)` | При ошибке повторить через 5 сек, максимум 3 раза |

!!! warning "Celery Worker — синхронный"
    Функция задачи — обычная Python-функция, **не** `async def`. Celery Worker работает синхронно. Поэтому используется `httpx.Client` (синхронный), а не `httpx.AsyncClient`.

---

## Эндпоинты FastAPI

### POST /api/parse/async — поставить задачу в очередь

```python
@router.post("/async")
def parse_async(request: ParseRequest):
    task = parse_url_task.delay(request.url)   # .delay() = асинхронный запуск
    return {"task_id": task.id, "status": "queued"}
```

`.delay(url)` — кладёт задачу в Redis и возвращает объект с `task.id`. Функция возвращается **мгновенно**, не дожидаясь выполнения.

### GET /api/parse/status/{task_id} — проверить статус

```python
@router.get("/status/{task_id}")
def parse_status(task_id: str):
    task = parse_url_task.AsyncResult(task_id)   # читает результат из Redis
    if task.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    if task.state == "FAILURE":
        return {"task_id": task_id, "status": "failure", "error": str(task.result)}
    return {"task_id": task_id, "status": task.state.lower(), "result": task.result}
```

Возможные значения `task.state`:

| Статус | Описание |
|--------|----------|
| `PENDING` | Задача ещё не взята воркером |
| `STARTED` | Воркер взял задачу и выполняет |
| `SUCCESS` | Выполнена успешно, `task.result` содержит результат |
| `FAILURE` | Ошибка после всех попыток retry, `task.result` — исключение |

---

## Docker Compose — сервисы Redis и Celery Worker

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    retries: 5

celery_worker:
  build: ./fastapi_app            # тот же образ что и fastapi
  command: celery -A celery_app worker --loglevel=info
  env_file: .env
  depends_on:
    redis:
      condition: service_healthy
    parser:
      condition: service_started
```

`celery -A celery_app worker` — запустить воркер, используя объект `celery_app` из файла `celery_app.py`.

---

## Проверка работы

### Через Swagger (http://localhost:8000/docs)

**Шаг 1.** `POST /api/parse/async`:
```json
{ "url": "https://github.com/topics?page=1" }
```
Ответ (мгновенно):
```json
{ "task_id": "b3f1a2c4-9e8d-...", "status": "queued" }
```

**Шаг 2.** `GET /api/parse/status/b3f1a2c4-9e8d-...`

Через 3–5 секунд:
```json
{
  "task_id": "b3f1a2c4-9e8d-...",
  "status": "success",
  "result": {
    "url": "https://github.com/topics?page=1",
    "count": 19,
    "results": ["JavaScript", "Python", "React", ...]
  }
}
```

### Через curl

```bash
# Поставить задачу
TASK=$(curl -s -X POST http://localhost:8000/api/parse/async \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/topics?page=1"}')

echo $TASK
# {"task_id":"b3f1a2c4-...","status":"queued"}

TASK_ID=$(echo $TASK | python3 -c "import sys,json; print(json.load(sys.stdin)['task_id'])")

# Подождать и проверить статус
sleep 5
curl http://localhost:8000/api/parse/status/$TASK_ID
```

### Логи воркера

```bash
docker compose logs celery_worker --tail=20
```

```
[INFO] Task parse_url_task[b3f1a2c4-...] received
[INFO] Task parse_url_task[b3f1a2c4-...] succeeded in 3.21s
```

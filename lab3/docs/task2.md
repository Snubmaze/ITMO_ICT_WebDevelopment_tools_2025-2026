# Задача 2 — HTTP-вызов парсера из FastAPI

**Цель:** добавить в FastAPI эндпоинт, который принимает URL от клиента, передаёт его парсер-сервису по HTTP и возвращает результат клиенту.

---

## Архитектура вызова

```
Клиент
  │  POST /api/parse {"url": "..."}
  ▼
FastAPI (:8000)
  │  POST http://parser:8001/parse {"url": "..."}
  ▼
Parser (:8001)
  │  aiohttp → scrape URL → BeautifulSoup
  │
  └──▶ {"url": "...", "count": 36, "results": [...]}
  ▲
FastAPI
  │
  └──▶ Клиент получает тот же ответ
```

Парсер — это отдельный микросервис с единственной ответственностью: получить URL, спарсить страницу, вернуть список. Он ничего не знает про базу данных и про FastAPI из lab1.

---

## Parser-сервис

### parser.py — логика парсинга

Логика парсинга из `lab2/task2/async_solution.py` вынесена в чистую функцию без побочных эффектов (без записи в БД):

```python
async def parse_url(url: str) -> list[str]:
    clean_url = url.split("#")[0]
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession() as session:
        async with session.get(clean_url, headers=HEADERS, timeout=timeout) as resp:
            resp.raise_for_status()
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")

    if "stackoverflow.com" in url:
        tags = soup.find_all("a", class_="post-tag")
        return [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

    if "github.com/topics" in url:
        items = soup.find_all("p", class_=lambda c: c and "f3" in c.split())
        return [p.get_text(strip=True) for p in items if p.get_text(strip=True)]

    if "wikipedia.org" in url:
        ...  # срез списка языков программирования

    # Произвольный URL — первые 50 текстовых ссылок
    links = soup.find_all("a")
    return [a.get_text(strip=True) for a in links if a.get_text(strip=True)][:50]
```

### main.py — FastAPI-обёртка

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from parser import parse_url

app = FastAPI(title="Parser Service")

class ParseRequest(BaseModel):
    url: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/parse")
async def parse(request: ParseRequest):
    try:
        results = await parse_url(request.url)
        return {"url": request.url, "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Эндпоинт в FastAPI

В основном приложении (lab1) добавлен новый роутер `app/api/routers/parser.py`.

Для HTTP-запросов к parser-сервису используется `httpx` — асинхронный HTTP-клиент, совместимый с FastAPI.

```python
@router.post("")   # POST /api/parse
async def parse_sync(request: ParseRequest):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.PARSER_URL}/parse",   # http://parser:8001/parse
                json={"url": request.url},
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Parser unavailable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
```

`settings.PARSER_URL` берётся из `.env`:
```env
PARSER_URL=http://parser:8001
```

`parser` — имя сервиса в docker-compose, Docker резолвит его во внутренний IP контейнера.

---

## Проверка работы

### Через Swagger

Открой **http://localhost:8000/docs**, найди `POST /api/parse`, нажми **Try it out**:

```json
{ "url": "https://stackoverflow.com/tags?page=1&tab=popular" }
```

### Через curl

```bash
curl -X POST http://localhost:8000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stackoverflow.com/tags?page=1&tab=popular"}'
```

### Ожидаемый ответ

```json
{
  "url": "https://stackoverflow.com/tags?page=1&tab=popular",
  "count": 36,
  "results": [
    "javascript",
    "python",
    "java",
    "c#",
    "php",
    ...
  ]
}
```

---

## Обработка ошибок

| Ситуация | HTTP-код | Описание |
|----------|----------|----------|
| Parser-сервис недоступен | `502` | `httpx.RequestError` — сеть или контейнер упал |
| Parser вернул ошибку | `4xx/5xx` | Прокидывается статус от parser-сервиса |
| Успех | `200` | Список спарсенных элементов |

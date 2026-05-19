# Задача 2 — Параллельный веб-парсинг

**Цель:** параллельно спарсить навыки (skills) с трёх веб-источников и сохранить их в таблицу `skills` базы данных `teamfinder` из Лабораторной работы 1.

---

## Источники данных

| # | Источник | URL | Что извлекается |
|---|----------|-----|-----------------|
| 1 | Stack Overflow Tags | `stackoverflow.com/tags?page=N&tab=popular` | Популярные теги технологий (36 на страницу) |
| 2 | GitHub Topics | `github.com/topics?page=N` | Названия технологических топиков |
| 3 | Wikipedia | `en.wikipedia.org/wiki/List_of_programming_languages` | Языки программирования (~775 на странице) |

Всего 12 URL: по 4 страницы от каждого источника. Wikipedia запрашивается 4 раза, каждый раз извлекается свой срез результата (через fragment `#0`–`#3`).

### Схема таблицы

```sql
CREATE TABLE skills (
    id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL
);
```

Дубликаты обрабатываются через `ON CONFLICT (name) DO NOTHING`.

---

## Подход 1 — threading

**Файл:** `task2/threading_solution.py`

### Описание

12 URL делятся на 4 равные части. Каждая часть обрабатывается отдельным потоком. Внутри потока URL обходятся последовательно: загрузка страницы → парсинг → запись в БД. Запись защищена `threading.Lock`, чтобы потоки не открывали одновременно несколько соединений с PostgreSQL.

### Схема работы

```
main()
├── chunk 0 → Thread-0: [SO p1, SO p2, GitHub p1]
├── chunk 1 → Thread-1: [SO p3, SO p4, GitHub p2]
├── chunk 2 → Thread-2: [GitHub p3, GitHub p4, Wikipedia#0]
└── chunk 3 → Thread-3: [Wikipedia#1, Wikipedia#2, Wikipedia#3]
    (потоки стартуют одновременно)
```

### Ключевые особенности

- GIL отпускается во время `requests.get` (сетевое ожидание), поэтому потоки реально работают параллельно на I/O
- `threading.Lock` на запись в БД сериализует сохранение — потоки выстраиваются в очередь при записи
- Открытие нового соединения psycopg2 на каждый URL внутри критической секции увеличивает время удержания блокировки

### Код

```python
def parse_and_save(url: str):
    skills = parse_url(url)          # сеть — без блокировки, параллельно
    with db_lock:                    # только один поток пишет в БД
        conn = get_connection()
        try:
            save_skills(conn, skills)
        finally:
            conn.close()
    print(f"[Threading] ✓ {len(skills):>3} навыков  ←  {url}")

def worker(urls_chunk: list):
    for url in urls_chunk:
        parse_and_save(url)
```

### Вывод программы

```
[Threading] ✓ 194 навыков  ←  .../List_of_programming_languages#1
[Threading] ✓  36 навыков  ←  stackoverflow.com/tags?page=1...
[Threading] ✓  36 навыков  ←  stackoverflow.com/tags?page=4...
[Threading] ✓ 194 навыков  ←  .../List_of_programming_languages#2
[Threading] ✓  36 навыков  ←  stackoverflow.com/tags?page=2...
[Threading] ✓ 197 навыков  ←  .../List_of_programming_languages#3
[Threading] ✓  36 навыков  ←  stackoverflow.com/tags?page=3...
[Threading] ✓  19 навыков  ←  github.com/topics?page=1
[Threading] ✓   3 навыков  ←  github.com/topics?page=3
[Threading] ✓   3 навыков  ←  github.com/topics?page=2
[Threading] ✓   3 навыков  ←  github.com/topics?page=4
[Threading] ✓ 194 навыков  ←  .../List_of_programming_languages#0

[Threading] Готово. Время: 5.5881 сек | Потоков: 4
```

---

## Подход 2 — multiprocessing

**Файл:** `task2/multiprocessing_solution.py`

### Описание

12 URL делятся на 4 части, каждая обрабатывается отдельным процессом `multiprocessing.Process`. Каждый процесс независим: свой интерпретатор, своё соединение с PostgreSQL. Для синхронизации записи используется `multiprocessing.Lock`, который передаётся в каждый процесс явно через аргументы.

### Схема работы

```
main()
├── Process-0: [SO p1, SO p2, GitHub p1]  ← своя память, свой Python
├── Process-1: [SO p3, SO p4, GitHub p2]
├── Process-2: [GitHub p3, GitHub p4, Wikipedia#0]
└── Process-3: [Wikipedia#1, Wikipedia#2, Wikipedia#3]
    (процессы работают независимо, Lock синхронизирует только DB-запись)
```

### Ключевые особенности

- Нет GIL: каждый процесс — независимый интерпретатор Python
- Реальный параллелизм на уровне ОС — несколько ядер ЦПУ
- `multiprocessing.Lock` работает через разделяемую память ОС (семафор)
- Overhead на старт процессов (~200–400 мс), но при сетевых задачах он компенсируется

### Код

```python
def worker(urls_chunk: list, lock):
    global _db_lock
    _db_lock = lock          # инициализируем глобальный lock в процессе
    for url in urls_chunk:
        parse_and_save(url)

def main():
    lock = multiprocessing.Lock()
    chunks = ...             # делим URLS на 4 части
    processes = [
        multiprocessing.Process(target=worker, args=(chunk, lock))
        for chunk in chunks
    ]
    for p in processes: p.start()
    for p in processes: p.join()
```

### Вывод программы

```
[Multiprocessing] ✓ 194 навыков  ←  .../List_of_programming_languages#1
[Multiprocessing] ✓ 194 навыков  ←  .../List_of_programming_languages#2
[Multiprocessing] ✓ 197 навыков  ←  .../List_of_programming_languages#3
[Multiprocessing] ✓   3 навыков  ←  github.com/topics?page=3
[Multiprocessing] ✓   3 навыков  ←  github.com/topics?page=4
[Multiprocessing] ✓ 194 навыков  ←  .../List_of_programming_languages#0
[Multiprocessing] ✓  36 навыков  ←  stackoverflow.com/tags?page=4...
[Multiprocessing] ✓  19 навыков  ←  github.com/topics?page=1
[Multiprocessing] ✓   3 навыков  ←  github.com/topics?page=2
[Multiprocessing] ✓  36 навыков  ←  stackoverflow.com/tags?page=1...
[Multiprocessing] ✓  36 навыков  ←  stackoverflow.com/tags?page=2...
[Multiprocessing] ✓  36 навыков  ←  stackoverflow.com/tags?page=3...

[Multiprocessing] Готово. Время: 1.6574 сек | Процессов: 4
```

---

## Подход 3 — async

**Файл:** `task2/async_solution.py`

### Описание

12 URL делятся на 4 группы. Для каждой группы запускается корутина-воркер, все воркеры запускаются одновременно через `asyncio.gather`. HTTP-запросы выполняются через `aiohttp.ClientSession`, запись в БД — через пул соединений `asyncpg`. Все операции не блокируют event loop — во время ожидания ответа от сервера выполняется другая корутина.

### Схема работы

```
asyncio.gather(worker0, worker1, worker2, worker3)
│
├── worker0 → parse_and_save(url1) → await GET → await INSERT
│              parse_and_save(url2) → await GET → ...
├── worker1 → ...          ↑ event loop переключается здесь
├── worker2 → ...
└── worker3 → ...
```

### Ключевые особенности

- Один поток, один процесс — нет накладных расходов на создание потоков/процессов
- `aiohttp` — асинхронный HTTP-клиент: `await session.get(url)` отпускает event loop
- `asyncpg` — асинхронный PostgreSQL-драйвер: `await conn.execute(...)` не блокирует
- Пул соединений `asyncpg.create_pool` позволяет нескольким корутинам писать в БД без очереди
- Масштабируется на сотни запросов без создания сотен потоков

### Код

```python
async def parse_and_save(session, pool, url):
    skills = await parse_url(session, url)   # не блокирует — ждём сеть
    await save_skills(pool, skills)           # не блокирует — ждём БД
    print(f"[Async] ✓ {len(skills):>3} навыков  ←  {url}")

async def main():
    pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=4)
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[
            worker(session, pool, chunk) for chunk in chunks
        ])
    await pool.close()
```

### Вывод программы

```
[Async] ✓   3 навыков  ←  github.com/topics?page=3
[Async] ✓ 194 навыков  ←  .../List_of_programming_languages#1
[Async] ✓  36 навыков  ←  stackoverflow.com/tags?page=1...
[Async] ✓  36 навыков  ←  stackoverflow.com/tags?page=4...
[Async] ✓   3 навыков  ←  github.com/topics?page=4
[Async] ✓ 194 навыков  ←  .../List_of_programming_languages#2
[Async] ✓  36 навыков  ←  stackoverflow.com/tags?page=2...
[Async] ✓ 194 навыков  ←  .../List_of_programming_languages#0
[Async] ✓  19 навыков  ←  github.com/topics?page=1
[Async] ✓  36 навыков  ←  stackoverflow.com/tags?page=3...
[Async] ✓ 197 навыков  ←  .../List_of_programming_languages#3
[Async] ✓   3 навыков  ←  github.com/topics?page=2

[Async] Готово. Время: 1.1454 сек | Воркеров: 4
```

---

## Сравнение результатов

| Подход | Время | Навыков сохранено | Параллелизм | Драйвер БД |
|--------|-------|-------------------|-------------|------------|
| `threading` | **5.5881 сек** | 951 | Псевдопараллельный (GIL) | psycopg2 (sync) |
| `multiprocessing` | **1.6574 сек** | 951 | Настоящий (4 процесса) | psycopg2 (sync) |
| `async` | **1.1454 сек** | 951 | Кооперативный (1 поток) | asyncpg (async) |

### Анализ

**Почему `threading` оказался медленнее всего** (5.59 сек против 1.66 у `multiprocessing`) — это неожиданный результат для I/O-bound задачи, где потоки теоретически должны работать хорошо. Причина — `db_lock` захватывается на весь цикл «открыть соединение → записать все навыки → закрыть соединение». Страница Wikipedia содержит ~194 навыка, запись которых занимает время. Пока один поток держит блокировку, остальные простаивают, даже если их HTTP-ответы уже получены. Это нивелирует параллелизм сети.

**Почему `multiprocessing` быстрее `threading`** — каждый процесс имеет собственное независимое соединение с PostgreSQL, никаких глобальных блокировок. Четыре процесса реально пишут в БД одновременно (PostgreSQL обрабатывает конкурентные соединения нативно). Overhead на запуск 4 процессов (~200 мс) меньше, чем потери от сериализации записи в threading.

**Почему `async` быстрее всего** — `asyncpg` с пулом соединений позволяет нескольким корутинам писать в БД без взаимного ожидания. Пока одна корутина ждёт `INSERT`, event loop переключается на другую, которая либо парсит HTML, либо ждёт другой DB-запрос. Нет overhead на создание потоков/процессов. Это классическая победа async на I/O-bound нагрузке.

!!! tip "Практический вывод"
    Для задач с сетевыми запросами и записью в БД **async** — оптимальный выбор: минимальный overhead, максимальный параллелизм I/O. `multiprocessing` хорош как запасной вариант, когда нужен реальный CPU-параллелизм. `threading` требует аккуратного дизайна блокировок — наивная реализация с глобальным `Lock` на весь DB-цикл уничтожает преимущества параллелизма.

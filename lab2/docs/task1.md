# Задача 1 — Параллельные вычисления

**Цель:** вычислить сумму всех целых чисел от 1 до 10 000 000 000 000, разбив задачу на 8 параллельных частей с помощью трёх подходов.

Правильный ответ: **50 000 000 000 005 000 000 000 000**

---

## Подход 1 — threading

**Файл:** `task1/multi_threading.py`

### Описание

Задача делится на 8 равных диапазонов. Для каждого диапазона запускается отдельный поток (`threading.Thread`). Каждый поток вычисляет сумму своего диапазона по формуле арифметической прогрессии и записывает результат в общий список `results` по своему индексу. После завершения всех потоков главный поток суммирует результаты.

### Особенности

- Потоки разделяют общую память — запись в `results[index]` безопасна без блокировок, так как каждый поток пишет в свою ячейку
- GIL не является проблемой: вычисление по формуле `n * (start + end) // 2` — одна операция Python, потоки не конкурируют за процессор
- Потоки создаются и запускаются последовательно, но выполняются параллельно

### Код

```python
import threading
import time

TOTAL = 10_000_000_000_000
NUM_THREADS = 8
results = [0] * NUM_THREADS

def calculate_sum(start: int, end: int, index: int):
    n = end - start + 1
    results[index] = n * (start + end) // 2

def main():
    chunk = TOTAL // NUM_THREADS
    threads = []
    start_time = time.perf_counter()

    for i in range(NUM_THREADS):
        start = i * chunk + 1
        end = (i + 1) * chunk if i < NUM_THREADS else TOTAL
        t = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    print(f"Результат: {total}")
    print(f"Время: {time.perf_counter() - start_time:.6f} сек")
```

### Результат

```
Результат: 50000000000005000000000000
Время работы алгоритма: 0.000342 сек
```

---

## Подход 2 — multiprocessing

**Файл:** `task1/multiprocess.py`

### Описание

Задача делится на 8 диапазонов, каждый обрабатывается отдельным процессом через `multiprocessing.Pool.starmap`. Каждый процесс имеет свою копию памяти и не зависит от GIL других процессов. Результаты возвращаются через механизм IPC (inter-process communication) и суммируются в главном процессе.

### Особенности

- Обходит GIL: каждый процесс запускает собственный интерпретатор Python
- Значительный overhead на старт процессов (~100 мс для 8 процессов)
- Данные между процессами передаются через сериализацию (pickle) — дополнительные затраты

### Код

```python
import multiprocessing
import time

TOTAL = 10_000_000_000_000
NUM_PROCESSES = 8

def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (end + start) // 2

def main():
    chunk = TOTAL // NUM_PROCESSES
    ranges = [(i * chunk + 1, (i + 1) * chunk) for i in range(NUM_PROCESSES)]

    start_time = time.perf_counter()
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        sub_res = pool.starmap(calculate_sum, ranges)

    total = sum(sub_res)
    print(f"Сумма: {total}")
    print(f"Время: {time.perf_counter() - start_time:.6f} сек")
```

### Результат

```
Сумма: 50000000000005000000000000
Время: 0.120925 сек
```

---

## Подход 3 — async

**Файл:** `task1/async_solution.py`

### Описание

Задача делится на 8 корутин, запускаемых через `asyncio.gather`. Каждая корутина вычисляет сумму своего диапазона по формуле и возвращает результат. Все корутины выполняются в одном потоке — никакого истинного параллелизма нет, но для мгновенных вычислений это не важно.

### Особенности

- Кооперативная многозадачность: один поток, корутины передают управление через `await`
- Здесь `await` фактически не используется внутри `calculate_sum` — функция выполняется синхронно, поэтому `asyncio.gather` не даёт параллелизма
- Минимальный overhead: нет создания потоков/процессов
- Подходит для I/O-bound задач, не для CPU-bound

### Код

```python
import asyncio
import time

TOTAL = 10_000_000_000_000
NUM_TASKS = 8

async def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (start + end) // 2

async def main():
    chunks = TOTAL // NUM_TASKS
    tasks = [
        asyncio.create_task(calculate_sum(i * chunks + 1, (i + 1) * chunks))
        for i in range(NUM_TASKS)
    ]
    start_time = time.perf_counter()
    sub_res = await asyncio.gather(*tasks)
    total = sum(sub_res)
    print(f"Сумма: {total}")
    print(f"Время: {time.perf_counter() - start_time:.6f} сек")
```

### Результат

```
Сумма: 50000000000005000000000000
Время: 0.000087 сек
```

---

## Сравнение результатов

| Подход | Время | Результат | Параллелизм |
|--------|-------|-----------|-------------|
| `threading` | 0.000342 сек | верный | Псевдопараллельный (GIL) |
| `multiprocessing` | 0.120925 сек | верный | Настоящий (отдельные процессы) |
| `async` | 0.000087 сек | верный | Кооперативный (один поток) |

### Анализ

`async` оказался быстрее всех — это контринтуитивный результат, объясняемый природой задачи. Формула арифметической прогрессии выполняется за одну операцию Python, поэтому все 8 «параллельных» вычислений занимают микросекунды. Накладные расходы `asyncio` (создание event loop, task scheduling) минимальны.

`threading` незначительно медленнее async из-за создания 8 объектов `Thread` и синхронизации через `join`.

`multiprocessing` оказался на два порядка медленнее: запуск 8 новых процессов Python на macOS занимает ~120 мс независимо от объёма работы. Для задач с мгновенными вычислениями это неприемлемо — overhead превышает полезную работу.

!!! note "Вывод"
    Для CPU-bound задач с **реальными** вычислениями (например, перебор чисел в цикле) `multiprocessing` обгонит остальные подходы за счёт использования всех ядер процессора. Здесь же задача сводится к одной арифметической операции, и преимущество теряется.

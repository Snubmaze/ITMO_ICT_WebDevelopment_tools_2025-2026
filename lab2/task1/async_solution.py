import asyncio
import time


TOTAL = 10_000_000_000_000
NUM_TASKS = 8


async def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (start + end) // 2


async def main():
    chunks = TOTAL // NUM_TASKS
    tasks = []

    for i in range(NUM_TASKS):
        start = i * chunks + 1
        end = (i + 1) * chunks if i < NUM_TASKS else TOTAL
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    start_time = time.perf_counter()
 
    sub_res = await asyncio.gather(*tasks)
 
    total = sum(sub_res)
    total_time = time.perf_counter() - start_time
 
    print(f"Сумма: {total}")
    print(f"Время: {total_time:.6f} сек")
 
 
if __name__ == "__main__":
    asyncio.run(main())






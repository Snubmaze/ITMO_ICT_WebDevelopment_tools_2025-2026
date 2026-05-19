import threading
import time


TOTAL = 10_000_000_000_000
NUM_THREADS = 8
 
results = [0] * NUM_THREADS


def calculate_sum(start: int, end: int, index: int) -> int:
    n = end - start + 1
    sub_res = n * (start + end) // 2
    results[index] = sub_res


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
        print(threads)

    for t in threads:
        t.join()
    
    total = sum(results)

    total_time = time.perf_counter() - start_time

    print(f"Результат: {total}")
    print(f"Время работы алгоритма: {total_time:.6f} сек")


if __name__ == "__main__":
    main()


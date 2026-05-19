import multiprocessing
import time


TOTAL = 10_000_000_000_000
NUM_PROCESSES = 8


def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (end + start ) // 2


def main():
    chunk = TOTAL // NUM_PROCESSES
    ranges = []
    
    for i in range(NUM_PROCESSES):
        start = i * chunk + 1
        end = (i + 1) * chunk if chunk < NUM_PROCESSES else TOTAL
        ranges.append((start, end))
    
    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        sub_res = pool.starmap(calculate_sum, ranges)

    
    total = sum(sub_res)
    total_time = time.perf_counter() - start_time
 
    print(f"Сумма: {total}")
    print(f"Время: {total_time:.6f} сек")
 
 
if __name__ == "__main__":
    main()
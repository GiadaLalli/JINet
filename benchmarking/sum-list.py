"""Python microbenchmark to compare native vs WASM performance."""

import os
import timeit
import csv
from pathlib import Path
import random


def sum_list(size: int) -> int:
    """Generate a random list then sum it."""
    data = random.sample(range(-1_000_000, 1_000_000), size)
    return sum(data)


def benchmark_function(params, num_runs):
    """Run the benchmark in a parameter sweep."""
    all_results = []

    for param in params:
        timer = timeit.Timer(lambda: sum_list(param))
        times = timer.repeat(repeat=num_runs, number=1)
        all_results.append(times)

    # Transpose the results to have parameters as columns
    return list(map(list, zip(*all_results)))


def main(unused):
    """Run the benchmark."""
    params = [10_000, 100_000, 1_000_000]
    results = benchmark_function(params, num_runs=100)
    # Write results to CSV
    name = Path(__file__).stem
    filename = f"Python-{name}-{os.uname().machine}.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(params)  # Write the parameter values as the header
        writer.writerows(results)

    return filename


# Run with: OPENBLAS_NUM_THREADS=1 python matrix-inverse.py
if __name__ == "__main__":
    main()

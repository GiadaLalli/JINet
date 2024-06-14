"""Python microbenchmark to compare native vs WASM performance."""

import os
import timeit
import csv
from pathlib import Path

from numpy import allclose, dot, eye
from numpy.random import rand
from numpy.linalg import inv


def invert_matrix(size: int):
    """Invert a matrix and test that it is correctly inverted."""
    matrix = rand(size, size)
    inverted = inv(matrix)
    assert allclose(dot(matrix, inverted), eye(size)) == True
    assert allclose(dot(inverted, matrix), eye(size)) == True
    return inverted


def benchmark_function(params, num_runs):
    """Run the benchmark in a parameter sweep."""
    all_results = []

    for param in params:
        print(f"Running {param}...", end="")
        timer = timeit.Timer(lambda: invert_matrix(param))
        times = timer.repeat(repeat=num_runs, number=1)
        all_results.append(times)
        print("[DONE]")

    # Transpose the results to have parameters as columns
    return list(map(list, zip(*all_results)))


def main(unused):
    """Run the benchmark."""
    params = [200, 500, 800]
    results = benchmark_function(params, num_runs=100)
    name = Path(__file__).stem
    filename = f"Python-{name}-{os.uname().machine}.csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(params)  # Write the parameter values as the header
        writer.writerows(results)

    return filename


# Run with: OPENBLAS_NUM_THREADS=1 python matrix-inverse.py
if __name__ == "__main__":
    main(1)

"""Plot the performance data."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main():
    for datafile in Path("data").iterdir():
        data = pd.read_csv(datafile)
        fig = plt.figure()
        data.boxplot()
        plt.title(datafile.stem)
        fig.savefig(f"{datafile.stem}.svg", format="svg")


def R_plot(benchmark, title, xlabel):
    wasm32 = pd.read_csv(f"data/R-{benchmark}-wasm32.csv")
    x86 = pd.read_csv(f"data/R-{benchmark}-x86_64.csv")
    y_max = max(wasm32.max().max(), x86.max().max())
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    wasm32.boxplot(ax=ax[0])
    x86.boxplot(ax=ax[1])
    ax[0].set_title("WASM32")
    ax[0].set_ylim([0, y_max])
    ax[0].set_ylabel("Time (seconds)")
    ax[0].set_xlabel(xlabel)
    ax[1].set_title("x86_64 Native")
    ax[1].set_ylim([0, y_max])
    ax[1].set_yticklabels([])
    ax[1].set_xlabel(xlabel)

    plt.tight_layout()
    fig.suptitle(title, fontsize=16)
    fig.savefig(f"R-{benchmark}.png", format="png")


def python_plot(benchmark, title, xlabel):
    wasm32 = pd.read_csv(f"data/Python-{benchmark}-wasm32.csv")
    x86 = pd.read_csv(f"data/Python-{benchmark}-x86_64.csv")
    y_max = max(wasm32.max().max(), x86.max().max())
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    wasm32.boxplot(ax=ax[0])
    x86.boxplot(ax=ax[1])
    ax[0].set_title("WASM32")
    ax[0].set_ylim([0, y_max])
    ax[0].set_ylabel("Time (seconds)")
    ax[0].set_xlabel(xlabel)
    ax[1].set_title("x86_64 Native")
    ax[1].set_ylim([0, y_max])
    ax[1].set_yticklabels([])
    ax[1].set_xlabel(xlabel)

    plt.tight_layout()
    fig.suptitle(title, fontsize=16)
    fig.savefig(f"Python-{benchmark}.png", format="png")


if __name__ == "__main__":
    R_plot("coin_flips", "Coin Flips Benchmark", "Number of coin flips")
    R_plot(
        "matrix-multiply",
        "Matrix Multiplication Benchmark",
        "Size of the square matrix",
    )

    python_plot(
        "matrix-inverse", "Invert matrix benchmark", "Size of the square matrix"
    )
    python_plot("sum-list", "Sum a random list benchmark", "Length of the list")

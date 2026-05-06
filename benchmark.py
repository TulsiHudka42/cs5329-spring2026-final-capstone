"""
benchmark.py
Runs timing and memory benchmarks for baseline and optimized IMDb title search.
"""

import argparse
import csv
import time
import tracemalloc
from pathlib import Path

from algorithms import (
    build_title_hash_index,
    extract_ids,
    hash_search_by_title,
    linear_search_by_title,
)
from data_loader import dataframe_to_records, load_data

DEFAULT_INPUT_SIZES = [10_000, 50_000, 100_000, 500_000, 1_000_000]
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
RESULTS_CSV = RESULTS_DIR / "benchmark_results.csv"


def measure_peak_memory_and_time(function, *args):
    """Measure elapsed time and peak memory while running a function."""
    tracemalloc.start()
    start_time = time.perf_counter()
    output = function(*args)
    elapsed = time.perf_counter() - start_time
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return output, elapsed, peak / (1024 * 1024)


def choose_query_titles(records: list[dict], query_count: int = 100) -> list[str]:
    """
    Choose deterministic query titles spread across the dataset.
    This avoids only testing one easy case.
    """
    if not records:
        return []

    if len(records) <= query_count:
        return [record["primaryTitle"] for record in records]

    step = max(1, len(records) // query_count)
    queries = [records[i]["primaryTitle"] for i in range(0, len(records), step)]
    return queries[:query_count]


def run_many_linear_queries(records: list[dict], queries: list[str]) -> list[set[str]]:
    return [extract_ids(linear_search_by_title(records, query)) for query in queries]


def run_many_hash_queries(index: dict[str, list[dict]], queries: list[str]) -> list[set[str]]:
    return [extract_ids(hash_search_by_title(index, query)) for query in queries]


def benchmark_input_size(input_size: int, query_count: int) -> dict:
    print(f"\nBenchmarking input size: {input_size:,} records")

    df = load_data(nrows=input_size)
    records = dataframe_to_records(df)
    actual_size = len(records)
    queries = choose_query_titles(records, query_count=query_count)

    if not queries:
        raise ValueError("No queries available. Dataset appears to be empty.")

    baseline_results, baseline_time, baseline_memory = measure_peak_memory_and_time(
        run_many_linear_queries,
        records,
        queries,
    )

    index, index_build_time, index_build_memory = measure_peak_memory_and_time(
        build_title_hash_index,
        records,
    )

    optimized_results, optimized_query_time, optimized_query_memory = measure_peak_memory_and_time(
        run_many_hash_queries,
        index,
        queries,
    )

    outputs_match = baseline_results == optimized_results
    if not outputs_match:
        raise AssertionError("Baseline and optimized results do not match.")

    total_optimized_time = index_build_time + optimized_query_time
    speedup_queries_only = baseline_time / optimized_query_time if optimized_query_time > 0 else float("inf")
    speedup_including_build = baseline_time / total_optimized_time if total_optimized_time > 0 else float("inf")

    row = {
        "input_size": actual_size,
        "query_count": len(queries),
        "baseline_time_sec": baseline_time,
        "baseline_peak_memory_mb": baseline_memory,
        "index_build_time_sec": index_build_time,
        "index_build_peak_memory_mb": index_build_memory,
        "optimized_query_time_sec": optimized_query_time,
        "optimized_query_peak_memory_mb": optimized_query_memory,
        "optimized_total_time_sec": total_optimized_time,
        "speedup_queries_only": speedup_queries_only,
        "speedup_including_build": speedup_including_build,
        "outputs_match": outputs_match,
    }

    print(f"Baseline query time: {baseline_time:.6f} sec")
    print(f"Index build time: {index_build_time:.6f} sec")
    print(f"Optimized query time: {optimized_query_time:.6f} sec")
    print(f"Outputs match: {outputs_match}")
    print(f"Query-only speedup: {speedup_queries_only:.2f}x")

    return row


def write_results(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_CSV, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved benchmark results to {RESULTS_CSV}")


def generate_charts() -> None:
    """Generate required empirical charts from benchmark_results.csv."""
    import pandas as pd
    import matplotlib.pyplot as plt

    if not RESULTS_CSV.exists():
        print("No benchmark CSV found, so charts were not generated.")
        return

    FIGURES_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RESULTS_CSV)

    plt.figure()
    plt.plot(df["input_size"], df["baseline_time_sec"], marker="o", label="Baseline linear search")
    plt.plot(df["input_size"], df["optimized_query_time_sec"], marker="o", label="Optimized hash search")
    plt.plot(df["input_size"], df["optimized_total_time_sec"], marker="o", label="Optimized including index build")
    plt.xlabel("Input size (records)")
    plt.ylabel("Time (seconds)")
    plt.title("Search Runtime Scaling")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "runtime_scaling.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(df["input_size"], df["baseline_peak_memory_mb"], marker="o", label="Baseline query")
    plt.plot(df["input_size"], df["index_build_peak_memory_mb"], marker="o", label="Hash index build")
    plt.plot(df["input_size"], df["optimized_query_peak_memory_mb"], marker="o", label="Optimized query")
    plt.xlabel("Input size (records)")
    plt.ylabel("Peak memory (MB)")
    plt.title("Memory Usage Scaling")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "memory_scaling.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(df["input_size"], df["speedup_queries_only"], marker="o")
    plt.xlabel("Input size (records)")
    plt.ylabel("Speedup factor")
    plt.title("Optimized Query Speedup Over Baseline")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "speedup.png", dpi=200)
    plt.close()

    print(f"Saved charts to {FIGURES_DIR}/")


def run_benchmark(input_sizes=None, query_count: int = 100, make_charts: bool = True) -> None:
    input_sizes = input_sizes or DEFAULT_INPUT_SIZES
    rows = []

    for size in input_sizes:
        rows.append(benchmark_input_size(size, query_count=query_count))

    write_results(rows)

    if make_charts:
        generate_charts()


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark IMDb title search algorithms.")
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=DEFAULT_INPUT_SIZES,
        help="Input sizes to benchmark, for example: --sizes 10000 50000 100000 500000 1000000",
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=100,
        help="Number of title lookups to run for each input size.",
    )
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_benchmark(input_sizes=args.sizes, query_count=args.queries, make_charts=not args.no_charts)

# Algorithms at Scale – Final Capstone

## Project Title
Scaling Movie Title Search using IMDb Dataset

---

## Project Overview
In this project, I use the IMDb Non-Commercial Dataset to study how search performance changes as the dataset becomes large.

The problem I solve is movie title lookup. Given a movie or TV title, the program searches the IMDb title records and returns matching entries.

I compare two approaches:

1. A baseline linear search that scans every record.
2. An optimized hash table index that maps each title to matching IMDb records.

The purpose is to show the difference between a naive O(n) approach and an optimized average O(1) lookup approach at scale.

---

## Dataset
I use the IMDb Non-Commercial Dataset:

- `title.basics.tsv`

This dataset contains millions of movie and TV title records with fields such as title type, title name, year, and genre.

---

## Dataset Setup
The full IMDb file is not included in this repository because it is over 1GB.

To run the full benchmark:

1. Go to: https://datasets.imdbws.com/
2. Download: `title.basics.tsv.gz`
3. Unzip the file:

   ```bash
   gunzip title.basics.tsv.gz
   ```

4. Place the file here:

   ```text
   data/title.basics.tsv
   ```

A small sample file is included only so the repository can run without the full dataset. Final benchmark results should be generated using the full IMDb dataset.

---

## Project Structure

```text
cs5329-spring2026-final-capstone/
├── data_loader.py      # Loads, parses, and cleans IMDb data
├── algorithms.py       # Baseline and optimized search algorithms
├── benchmark.py        # Runs timing and memory benchmarks
├── main.py             # Entry point for full benchmark
├── requirements.txt    # Python dependencies
├── README.md           # Project instructions
├── report.md           # Analytical report draft/template
├── data/               # Sample data only; full dataset is ignored by git
├── results/            # Benchmark CSV output
└── figures/            # Generated runtime and memory charts
```

---

## Algorithms Implemented

### Baseline: Linear Search
The baseline checks each record one by one until it finds titles matching the query.

- Build time: none
- Query time: O(n)
- Extra space: O(k), where k is the number of matching records

### Optimized: Hash Table Index
The optimized approach first builds a dictionary where each normalized title points to matching IMDb records.

- Build time: O(n)
- Average query time: O(1 + k)
- Extra space: O(n)

This creates an upfront indexing cost, but repeated queries become much faster.

---

## Benchmarking
The benchmark script measures:

- Execution time
- Peak memory usage using `tracemalloc`
- Results across at least 5 input sizes
- Output correctness by checking that baseline and optimized results match

Default input sizes:

```text
10K, 50K, 100K, 500K, 1M records
```

---

## How to Run

1. Install dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Make sure the full dataset is placed at:

   ```text
   data/title.basics.tsv
   ```

3. Run the full benchmark:

   ```bash
   python3 main.py
   ```

4. Or run custom benchmark sizes:

   ```bash
   python3 benchmark.py --sizes 10000 50000 100000 500000 1000000 --queries 100
   ```

---

## Outputs
After running the benchmark, the program creates:

```text
results/benchmark_results.csv
figures/runtime_scaling.png
figures/memory_scaling.png
figures/speedup.png
```

---

## Author
Tulsi Hudka  
MS Computer Science – Texas State University
# cs5329-spring2026-final-capstone
# cs5329-spring2026-final-capstone

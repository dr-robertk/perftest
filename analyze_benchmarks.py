#!/usr/bin/env python3
"""Pull benchmark results from Supabase and print a summary.

Usage:
    python analyze_benchmarks.py           # quick row-count status
    python analyze_benchmarks.py --full    # full per-run table + breakdowns

Reads SUPABASE_DB_URL from the environment, or from a .env file in the
current directory (never committed - see .gitignore) if not already set.
"""

import argparse
import os

import pandas as pd
import psycopg2


def _load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

QUERY = """
SELECT
    r.id AS run_id,
    r.commit_sha,
    r.branch,
    r.python_version,
    r.cpu_brand,
    r.cpu_count,
    r.ci_run_id,
    r.ingested_at,
    b.name,
    b.grid_n,
    b.mean_seconds,
    b.stddev_seconds,
    b.min_seconds,
    b.max_seconds,
    b.median_seconds,
    b.rounds,
    b.ops
FROM benchmarks b
JOIN runs r ON r.id = b.run_id
ORDER BY r.ingested_at, b.name;
"""


def print_status(df: pd.DataFrame) -> None:
    print(f"{len(df)} benchmark rows across {df['run_id'].nunique()} runs")
    print(df.groupby("python_version")["run_id"].nunique().rename("runs"))
    print(f"time range: {df['ingested_at'].min()} .. {df['ingested_at'].max()}")
    print(
        f"distinct CPU models observed: {df['cpu_brand'].nunique()} "
        f"(min {df.groupby('cpu_brand')['run_id'].nunique().min()} runs/model)"
    )


def main() -> None:
    _load_dotenv()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="print the full per-run table and breakdowns (default: quick status only)",
    )
    args = parser.parse_args()

    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        raise SystemExit("Set SUPABASE_DB_URL, or put it in a .env file")

    conn = psycopg2.connect(db_url)
    try:
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", None)

    if not args.full:
        print_status(df)
        return

    print(f"\n{len(df)} benchmark rows across {df['run_id'].nunique()} runs\n")
    print(
        df[
            [
                "run_id",
                "python_version",
                "name",
                "grid_n",
                "mean_seconds",
                "stddev_seconds",
                "rounds",
            ]
        ]
    )

    print("\nSummary by test name + grid size:")
    print(
        df.groupby(["name", "grid_n"])["mean_seconds"]
        .agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )

    print("\nSummary by Python version:")
    print(df.groupby("python_version")["mean_seconds"].agg(["count", "mean", "std"]))

    print("\nSummary by CPU model (runs, not benchmark rows):")
    cpu_runs = df.drop_duplicates("run_id")
    print(
        cpu_runs.groupby("cpu_brand")["run_id"]
        .nunique()
        .rename("runs")
        .sort_values(ascending=False)
    )

    print("\nSummary by CPU model + test name:")
    print(
        df.groupby(["cpu_brand", "name"])["mean_seconds"]
        .agg(["count", "mean", "std"])
        .reset_index()
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pull benchmark results from Supabase and print a summary.

Usage:
    SUPABASE_DB_URL=postgresql://... python analyze_benchmarks.py
"""

import os

import pandas as pd
import psycopg2

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


def main() -> None:
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        raise SystemExit("Set SUPABASE_DB_URL first")

    conn = psycopg2.connect(db_url)
    try:
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", None)

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


if __name__ == "__main__":
    main()

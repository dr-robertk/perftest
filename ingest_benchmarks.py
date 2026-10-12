#!/usr/bin/env python3
"""Ingest pytest-benchmark JSON output into a Supabase (Postgres) database.

Usage:
    SUPABASE_DB_URL=postgresql://... python ingest_benchmarks.py benchmark-*.json
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id BIGSERIAL PRIMARY KEY,
    ingested_at TIMESTAMPTZ NOT NULL,
    source_file TEXT NOT NULL,

    -- from pytest-benchmark's commit_info
    commit_sha TEXT,
    commit_time TEXT,
    branch TEXT,
    dirty BOOLEAN,

    -- from pytest-benchmark's machine_info
    hostname TEXT,
    os_system TEXT,
    os_release TEXT,
    machine TEXT,
    python_version TEXT,
    python_implementation TEXT,
    cpu_brand TEXT,
    cpu_arch TEXT,
    cpu_count INTEGER,

    -- "server parameters": not in the benchmark JSON itself, read from the
    -- CI environment at ingestion time (GitHub Actions runner identity)
    ci_provider TEXT,
    ci_run_id TEXT,
    ci_run_attempt TEXT,
    ci_job TEXT,
    ci_workflow TEXT,
    runner_name TEXT,
    runner_os TEXT,
    runner_arch TEXT,

    UNIQUE (commit_sha, python_version, ci_run_id, ci_job)
);

CREATE TABLE IF NOT EXISTS benchmarks (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs (id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    fullname TEXT,

    min_seconds DOUBLE PRECISION,
    max_seconds DOUBLE PRECISION,
    mean_seconds DOUBLE PRECISION,
    median_seconds DOUBLE PRECISION,
    stddev_seconds DOUBLE PRECISION,
    iqr_seconds DOUBLE PRECISION,
    ops DOUBLE PRECISION,
    rounds INTEGER,
    total_seconds DOUBLE PRECISION,
    data_json JSONB,

    -- code-level configuration the test recorded via benchmark.extra_info,
    -- e.g. the PDE grid size (n) used for that run
    grid_n INTEGER,
    extra_info_json JSONB,

    UNIQUE (run_id, fullname)
);

CREATE INDEX IF NOT EXISTS idx_benchmarks_name ON benchmarks (name);
CREATE INDEX IF NOT EXISTS idx_runs_commit ON runs (commit_sha);
"""


def create_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()


def run_fields(payload: dict, source_file: str) -> dict:
    commit = payload.get("commit_info") or {}
    machine = payload.get("machine_info") or {}
    cpu = machine.get("cpu") or {}

    return {
        "ingested_at": datetime.now(timezone.utc),
        "source_file": source_file,
        "commit_sha": commit.get("id"),
        "commit_time": commit.get("time"),
        "branch": commit.get("branch"),
        "dirty": bool(commit.get("dirty")),
        "hostname": machine.get("node"),
        "os_system": machine.get("system"),
        "os_release": machine.get("release"),
        "machine": machine.get("machine"),
        "python_version": machine.get("python_version"),
        "python_implementation": machine.get("python_implementation"),
        "cpu_brand": cpu.get("brand_raw"),
        "cpu_arch": cpu.get("arch"),
        "cpu_count": cpu.get("count"),
        "ci_provider": "github" if os.environ.get("GITHUB_ACTIONS") else None,
        "ci_run_id": os.environ.get("GITHUB_RUN_ID"),
        "ci_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "ci_job": os.environ.get("GITHUB_JOB"),
        "ci_workflow": os.environ.get("GITHUB_WORKFLOW"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
    }


def benchmark_rows(payload: dict) -> list[dict]:
    rows = []
    for bench in payload.get("benchmarks", []):
        stats = bench.get("stats") or {}
        extra_info = bench.get("extra_info") or {}
        rows.append(
            {
                "name": bench.get("name"),
                "fullname": bench.get("fullname"),
                "min_seconds": stats.get("min"),
                "max_seconds": stats.get("max"),
                "mean_seconds": stats.get("mean"),
                "median_seconds": stats.get("median"),
                "stddev_seconds": stats.get("stddev"),
                "iqr_seconds": stats.get("iqr"),
                "ops": stats.get("ops"),
                "rounds": stats.get("rounds"),
                "total_seconds": stats.get("total"),
                "data_json": psycopg2.extras.Json(stats["data"])
                if "data" in stats
                else None,
                "grid_n": extra_info.get("n"),
                "extra_info_json": psycopg2.extras.Json(extra_info),
            }
        )
    return rows


def ingest_file(conn, path: Path) -> None:
    payload = json.loads(path.read_text())
    run = run_fields(payload, source_file=path.name)

    with conn.cursor() as cur:
        cur.execute(
            """SELECT id FROM runs
               WHERE commit_sha IS %(commit_sha)s
                 AND python_version IS %(python_version)s
                 AND ci_run_id IS %(ci_run_id)s
                 AND ci_job IS %(ci_job)s""",
            run,
        )
        existing = cur.fetchone()
        if existing:
            print(f"  already ingested as run_id={existing[0]}, skipping")
            return

        columns = ", ".join(run)
        placeholders = ", ".join(f"%({k})s" for k in run)
        cur.execute(
            f"INSERT INTO runs ({columns}) VALUES ({placeholders}) RETURNING id",
            run,
        )
        run_id = cur.fetchone()[0]

        for row in benchmark_rows(payload):
            row["run_id"] = run_id
            columns = ", ".join(row)
            placeholders = ", ".join(f"%({k})s" for k in row)
            cur.execute(
                f"INSERT INTO benchmarks ({columns}) VALUES ({placeholders})", row
            )

    conn.commit()
    print(
        f"  ingested run_id={run_id} ({len(payload.get('benchmarks', []))} benchmarks)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "json_files", nargs="+", type=Path, help="pytest-benchmark JSON file(s)"
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("SUPABASE_DB_URL"),
        help="Postgres connection string (defaults to $SUPABASE_DB_URL)",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise SystemExit("No database URL given: pass --db-url or set SUPABASE_DB_URL")

    conn = psycopg2.connect(args.db_url)
    try:
        create_schema(conn)
        for path in args.json_files:
            print(f"Ingesting {path} ...")
            ingest_file(conn, path)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

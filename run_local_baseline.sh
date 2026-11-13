#!/bin/sh
# Entrypoint for the local-baseline container: repeatedly runs the benchmark
# suite and ingests the results into Supabase, tagged ci_provider='local' by
# ingest_benchmarks.py so they're distinguishable from passive CI data.
set -eu

INTERVAL="${BASELINE_INTERVAL_SECONDS:-3600}"

while true; do
    timestamp=$(date +%s)
    json_file="local-${timestamp}.json"

    echo "[$(date -Iseconds)] running benchmark suite..."
    if pytest --benchmark-only --benchmark-json="$json_file"; then
        python ingest_benchmarks.py "$json_file"
    else
        echo "[$(date -Iseconds)] pytest failed, skipping ingestion" >&2
    fi
    rm -f "$json_file"

    echo "[$(date -Iseconds)] sleeping ${INTERVAL}s..."
    sleep "$INTERVAL"
done

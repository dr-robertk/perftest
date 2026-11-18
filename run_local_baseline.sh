#!/bin/sh
# Entrypoint for the local-baseline container: repeatedly runs the benchmark
# suite and ingests the results into Supabase, tagged ci_provider='local' by
# ingest_benchmarks.py so they're distinguishable from passive CI data.
set -eu

INTERVAL="${BASELINE_INTERVAL_SECONDS:-3600}"

# One-time platform characterization (BLAS threading, perf/SMT/frequency
# availability) - same script as the CI diagnostic step, tagged
# ci_provider='local' automatically. Platform characteristics don't change
# between loop iterations on the same dedicated machine, so this runs once
# at container startup, not on every cycle.
echo "[$(date -Iseconds)] running platform diagnostics..."
python check_platform_diagnostics.py || echo "[$(date -Iseconds)] platform diagnostics failed, continuing anyway" >&2

while true; do
    timestamp=$(date +%s)
    json_file="local-${timestamp}.json"

    echo "[$(date -Iseconds)] running benchmark suite..."

    # Same /proc/stat "steal" measurement as testall.yml, for consistency -
    # on this dedicated, non-virtualized host it should read ~0%, which is
    # itself a useful confirmation that the baseline is actually contention-free.
    read -r _ u1 n1 s1 i1 w1 irq1 sirq1 st1 _ < /proc/stat
    total1=$((u1+n1+s1+i1+w1+irq1+sirq1+st1))

    if pytest --benchmark-only --benchmark-json="$json_file"; then
        read -r _ u2 n2 s2 i2 w2 irq2 sirq2 st2 _ < /proc/stat
        total2=$((u2+n2+s2+i2+w2+irq2+sirq2+st2))
        steal_delta=$((st2 - st1))
        total_delta=$((total2 - total1))
        if [ "$total_delta" -gt 0 ]; then
            STEAL_PCT=$(awk -v s="$steal_delta" -v t="$total_delta" 'BEGIN { printf "%.4f", (s/t)*100 }')
        else
            STEAL_PCT="0"
        fi
        export STEAL_PCT
        python ingest_benchmarks.py "$json_file"
    else
        echo "[$(date -Iseconds)] pytest failed, skipping ingestion" >&2
    fi
    rm -f "$json_file"

    echo "[$(date -Iseconds)] sleeping ${INTERVAL}s..."
    sleep "$INTERVAL"
done

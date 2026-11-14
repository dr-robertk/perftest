#!/usr/bin/env python3
"""One-off diagnostic: checks which hardware-contention measurement channels
(perf counters, SMT topology, live CPU frequency) are actually available on
this runner, and records the findings in Supabase for later inspection.

Usage:
    python check_platform_diagnostics.py
"""

import json
import os
import subprocess
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras


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


def check_perf() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [
                "perf", "stat", "-e", "cache-misses,cache-references,cycles,instructions",
                "--", "sleep", "1",
            ],
            capture_output=True, text=True, timeout=10,
        )
        output = (result.stdout + result.stderr).strip()
        # perf can exit 0 while still reporting it couldn't access the
        # counters, so check the text, not just the return code.
        lowered = output.lower()
        ok = (
            result.returncode == 0
            and "not supported" not in lowered
            and "permission" not in lowered
            and "<not counted>" not in lowered
        )
        return ok, output[:2000]
    except FileNotFoundError:
        return False, "perf: command not found"
    except Exception as e:
        return False, f"perf failed: {e}"


def check_topology() -> dict:
    try:
        result = subprocess.run(["lscpu", "-J"], capture_output=True, text=True, timeout=5)
        data = json.loads(result.stdout)
        fields = {entry["field"].rstrip(":"): entry["data"] for entry in data["lscpu"]}
        threads_per_core = int(fields.get("Thread(s) per core", "1"))
        return {
            "threads_per_core": threads_per_core,
            "smt_enabled": threads_per_core > 1,
            "cpu_model_name": fields.get("Model name"),
        }
    except Exception as e:
        return {"threads_per_core": None, "smt_enabled": None, "error": str(e)}


def check_frequency() -> dict:
    paths = [
        "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq",
        "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq",
    ]
    result = {}
    for path in paths:
        try:
            with open(path) as f:
                result[os.path.basename(path)] = int(f.read().strip())
        except (FileNotFoundError, PermissionError):
            result[os.path.basename(path)] = None

    # Cross-check against /proc/cpuinfo's reported MHz.
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.lower().startswith("cpu mhz"):
                    result["proc_cpuinfo_mhz"] = float(line.split(":")[1].strip())
                    break
    except Exception:
        pass
    return result


def main() -> None:
    _load_dotenv()
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        raise SystemExit("Set SUPABASE_DB_URL, or put it in a .env file")

    perf_ok, perf_output = check_perf()
    topo = check_topology()
    freq = check_frequency()

    print("perf available:", perf_ok)
    print("perf output:", perf_output)
    print("topology:", topo)
    print("frequency:", freq)

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS platform_diagnostics (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL,
                    ci_run_id TEXT,
                    perf_available BOOLEAN,
                    perf_output TEXT,
                    smt_enabled BOOLEAN,
                    threads_per_core INTEGER,
                    cpu_model_name TEXT,
                    frequency_info JSONB
                )
                """
            )
            cur.execute(
                """
                INSERT INTO platform_diagnostics
                    (created_at, ci_run_id, perf_available, perf_output,
                     smt_enabled, threads_per_core, cpu_model_name, frequency_info)
                VALUES (%(created_at)s, %(ci_run_id)s, %(perf_available)s, %(perf_output)s,
                        %(smt_enabled)s, %(threads_per_core)s, %(cpu_model_name)s, %(frequency_info)s)
                """,
                {
                    "created_at": datetime.now(timezone.utc),
                    "ci_run_id": os.environ.get("GITHUB_RUN_ID"),
                    "perf_available": perf_ok,
                    "perf_output": perf_output,
                    "smt_enabled": topo.get("smt_enabled"),
                    "threads_per_core": topo.get("threads_per_core"),
                    "cpu_model_name": topo.get("cpu_model_name"),
                    "frequency_info": psycopg2.extras.Json(freq),
                },
            )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()

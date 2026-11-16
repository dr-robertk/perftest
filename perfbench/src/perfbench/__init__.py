from perfbench.machine_info import load_machine_info
from perfbench.runner import (
    run_anchor_benchmarks,
    run_benchmarks,
    run_software_benchmarks,
    write_report,
)


__all__ = [
    "load_machine_info",
    "run_anchor_benchmarks",
    "run_benchmarks",
    "run_software_benchmarks",
    "write_report",
]


def main() -> None:
    report = run_anchor_benchmarks()
    write_report(report, "benchmark.json")
    for suite, benchmarks in report["benchmark_info"].items():
        for benchmark in benchmarks:
            stats = benchmark["stats"]
            print(
                f"{suite}/{benchmark['name']}: "
                f"mean={stats['mean']:.6f}s "
                f"stddev={stats['stddev']:.6f}s "
                f"rounds={stats['rounds']}"
            )
    print("Wrote benchmark.json")

import pprint

from room_solver.solver import solveDirichletNeumann

from perfbench import run_benchmarks, write_report


def main() -> None:
    report = run_benchmarks(
        {
            "room_solver": lambda: solveDirichletNeumann(n=101),
        },
        rounds=10,
        iterations=1,
        warmup_iterations=5,
        matmul_size=6500,
        memcopy_size=160_000_000,
    )

    pprint.pprint(report["machine_info"])
    pprint.pprint(report["benchmark_info"]["anchors"])
    pprint.pprint(report["benchmark_info"]["software"])
    write_report(report, "benchmark.json")


if __name__ == "__main__":
    main()

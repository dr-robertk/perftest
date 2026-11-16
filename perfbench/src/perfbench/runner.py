import json
import os
import statistics
import subprocess
import timeit
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from perfbench.anchors import matmul_anchor, memcopy_anchor
from perfbench.machine_info import load_machine_info

type BenchmarkResult = dict[str, object]


def _load_commit_info() -> dict[str, object]:
    working_directory = Path.cwd()
    root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=working_directory,
        capture_output=True,
        text=True,
        check=False,
    )
    if root_result.returncode:
        return {
            "id": "unversioned",
            "time": None,
            "author_time": None,
            "dirty": False,
            "project": working_directory.name,
            "branch": "(unknown)",
            "error": root_result.stderr.strip() or "Not inside a Git repository",
        }

    repository_root = Path(root_result.stdout.strip())
    commit_fields = subprocess.check_output(
        ["git", "log", "-1", "--format=%H%n%cI%n%aI"],
        cwd=repository_root,
        text=True,
    ).splitlines()
    if len(commit_fields) != 3:
        raise RuntimeError("Git returned incomplete commit metadata.")

    branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=repository_root,
        text=True,
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=repository_root,
            text=True,
        ).strip()
    )
    return {
        "id": commit_fields[0],
        "time": commit_fields[1],
        "author_time": commit_fields[2],
        "dirty": dirty,
        "project": repository_root.name,
        "branch": branch or "(detached head)",
    }


@dataclass(frozen=True)
class _BenchmarkTarget:
    suite: str
    name: str
    function: Callable[[], object]
    rounds: int
    iterations: int
    warmup_iterations: int
    extra_info: dict[str, object] = field(default_factory=dict)


def _measure(target: _BenchmarkTarget) -> BenchmarkResult:
    for _ in range(target.warmup_iterations):
        target.function()

    timer = timeit.Timer(target.function)
    samples = [
        elapsed / target.iterations
        for elapsed in timer.repeat(
            repeat=target.rounds,
            number=target.iterations,
        )
    ]
    mean = statistics.fmean(samples)
    stats: dict[str, object] = {
        "min": min(samples),
        "max": max(samples),
        "mean": mean,
        "median": statistics.median(samples),
        "stddev": statistics.stdev(samples) if len(samples) > 1 else 0.0,
        "rounds": target.rounds,
        "iterations": target.iterations,
        "warmup_iterations": target.warmup_iterations,
        "total": sum(samples) * target.iterations,
        "ops": 1 / mean if mean else None,
        "data": samples,
    }
    return {
        "name": target.name,
        "fullname": f"{target.suite}::{target.name}",
        "extra_info": {
            "suite": target.suite,
            "target": target.name,
            **target.extra_info,
        },
        "stats": stats,
    }


def run_benchmarks(
    software_benchmarks: Mapping[str, Callable[[], object]] | None = None,
    *,
    include_anchors: bool = True,
    rounds: int = 10,
    iterations: int = 1,
    warmup_iterations: int = 0,
    matmul_size: int = 5120,
    memcopy_size: int = 80_000_000,
) -> dict[str, object]:
    """Run anchor benchmarks and optional zero-argument software callables.

    Returns machine metadata and per-call timing summaries grouped into
    ``benchmark_info["anchors"]`` and ``benchmark_info["software"]``.
    """
    if rounds < 1 or iterations < 1 or warmup_iterations < 0:
        raise ValueError(
            "rounds and iterations must be positive, and warmup_iterations must be non-negative"
        )

    targets: list[_BenchmarkTarget] = []
    if include_anchors:
        if matmul_size < 1 or memcopy_size < 1:
            raise ValueError("anchor sizes must both be positive")
        targets.extend(
            [
                _BenchmarkTarget(
                    "anchors",
                    "matmul",
                    lambda: matmul_anchor(n=matmul_size),
                    rounds,
                    iterations,
                    warmup_iterations,
                    {"n": matmul_size},
                ),
                _BenchmarkTarget(
                    "anchors",
                    "memcopy",
                    lambda: memcopy_anchor(n=memcopy_size),
                    rounds,
                    iterations,
                    warmup_iterations,
                    {"n": memcopy_size},
                ),
            ]
        )

    for name, function in (software_benchmarks or {}).items():
        if not name or not callable(function):
            raise ValueError(
                "software benchmarks must have non-empty names and callable values"
            )
        targets.append(
            _BenchmarkTarget(
                "software",
                name,
                function,
                rounds,
                iterations,
                warmup_iterations,
            )
        )

    if not targets:
        raise ValueError("At least one anchor or software benchmark is required")

    benchmark_info: dict[str, list[BenchmarkResult]] = {
        "anchors": [],
        "software": [],
    }
    for target in targets:
        benchmark_info[target.suite].append(_measure(target))

    return {
        "machine_info": load_machine_info(),
        "commit_info": _load_commit_info(),
        "benchmark_info": benchmark_info,
    }


def run_anchor_benchmarks(
    *,
    rounds: int = 10,
    iterations: int = 1,
    warmup_iterations: int = 0,
    matmul_size: int = 5120,
    memcopy_size: int = 80_000_000,
) -> dict[str, object]:
    """Run only perfbench's built-in anchor benchmarks."""
    return run_benchmarks(
        include_anchors=True,
        rounds=rounds,
        iterations=iterations,
        warmup_iterations=warmup_iterations,
        matmul_size=matmul_size,
        memcopy_size=memcopy_size,
    )


def run_software_benchmarks(
    software_benchmarks: Mapping[str, Callable[[], object]],
    *,
    rounds: int = 10,
    iterations: int = 1,
    warmup_iterations: int = 0,
) -> dict[str, object]:
    """Benchmark named zero-argument callables without running anchors."""
    return run_benchmarks(
        software_benchmarks,
        include_anchors=False,
        rounds=rounds,
        iterations=iterations,
        warmup_iterations=warmup_iterations,
    )


def write_report(report: Mapping[str, object], path: str | os.PathLike[str]) -> None:
    """Write a benchmark report as formatted JSON."""
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")

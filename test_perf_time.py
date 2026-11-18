import pytest

from config import N
from singleThread import solveDirichletNeumann


def test_process_data(benchmark):
    benchmark.extra_info["n"] = N
    result = benchmark.pedantic(solveDirichletNeumann, iterations=2, rounds=20)

    assert len(result) == 3


def test_process_data_large(benchmark):
    n = 301
    benchmark.extra_info["n"] = n
    result = benchmark.pedantic(
        lambda: solveDirichletNeumann(n=n), iterations=1, rounds=10
    )

    assert len(result) == 3


@pytest.mark.benchmark(disable_gc=True)
def test_process_data_large_gc_disabled(benchmark):
    # Same solver, same grid size, same rounds/iterations as
    # test_process_data_large - the only difference is GC disabled during
    # timed rounds. Kept as a separate test, not a modification of the
    # original, so the two can be compared directly: does disabling GC
    # measurably tighten the within-model noise we've been trying to
    # explain via steal time and (eventually) CPU frequency?
    n = 301
    benchmark.extra_info["n"] = n
    result = benchmark.pedantic(
        lambda: solveDirichletNeumann(n=n), iterations=1, rounds=10
    )

    assert len(result) == 3


def test_process_data_extra_large(benchmark):
    n = 401
    benchmark.extra_info["n"] = n
    result = benchmark.pedantic(
        lambda: solveDirichletNeumann(n=n), iterations=1, rounds=10
    )

    assert len(result) == 3

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


def test_process_data_extra_large(benchmark):
    n = 401
    benchmark.extra_info["n"] = n
    result = benchmark.pedantic(
        lambda: solveDirichletNeumann(n=n), iterations=1, rounds=10
    )

    assert len(result) == 3

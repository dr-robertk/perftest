from singleThread import solveDirichletNeumann


def test_process_data(benchmark):
    result = benchmark.pedantic(solveDirichletNeumann, iterations=2, rounds=20)

    assert len(result) == 3

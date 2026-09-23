from bisection import bisect


def process_data(items):
    return sorted(x * 2 for x in items)


def test_process_data(benchmark):
    items = list(range(10_000))

    result = benchmark(process_data, items)

    assert len(result) == 10_000

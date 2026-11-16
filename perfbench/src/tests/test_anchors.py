from perfbench.anchors import matmul_anchor, memcopy_anchor


def test_anchor_matmul(benchmark):
    n = 5120
    benchmark.extra_info["n"] = n
    result = benchmark.pedantic(lambda: matmul_anchor(n=n), iterations=1, rounds=10)

    assert result.shape == (n, n)


def test_anchor_memcopy(benchmark):
    n = 80_000_000
    benchmark.extra_info["n"] = n
    result = benchmark.pedantic(lambda: memcopy_anchor(n=n), iterations=1, rounds=10)

    assert result.shape == (n,)

from anchor_matmul import matmul_anchor
from anchor_memcopy import memcopy_anchor
from anchor_memcopy_optimized import N as MEMCOPY_OPTIMIZED_N
from anchor_memcopy_optimized import memcopy_anchor_optimized


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


def test_anchor_memcopy_optimized(benchmark):
    benchmark.extra_info["n"] = MEMCOPY_OPTIMIZED_N
    result = benchmark.pedantic(memcopy_anchor_optimized, iterations=1, rounds=10)

    assert result.shape == (MEMCOPY_OPTIMIZED_N,)

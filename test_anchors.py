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
    # Unlike the other anchors, a single call here is only ~55-190ms (no
    # allocation overhead left to pad it out), short enough that fixed
    # per-call costs (timer resolution, dispatch overhead) may dominate the
    # measurement proportionally. iterations=10 batches 10 calls per timed
    # sample (pytest-benchmark divides the batch time by 10 for the
    # reported per-call mean), bringing the measured duration back to
    # ~0.5-1.9s - the same order of magnitude as the other anchors - without
    # reintroducing any allocation.
    benchmark.extra_info["n"] = MEMCOPY_OPTIMIZED_N
    result = benchmark.pedantic(memcopy_anchor_optimized, iterations=10, rounds=10)

    assert result.shape == (MEMCOPY_OPTIMIZED_N,)


def test_anchor_memcopy_optimized_iter30(benchmark):
    # Same anchor as test_anchor_memcopy_optimized, batched 30 calls per
    # timed sample instead of 10 - a separate test name (and thus its own
    # rows, distinguished further by the recorded `iterations` value) so we
    # can compare noise across batch sizes on real CI without losing the
    # iterations=10 data already collected.
    benchmark.extra_info["n"] = MEMCOPY_OPTIMIZED_N
    result = benchmark.pedantic(memcopy_anchor_optimized, iterations=30, rounds=10)

    assert result.shape == (MEMCOPY_OPTIMIZED_N,)


def test_anchor_memcopy_optimized_iter100(benchmark):
    # Same anchor again, batched 100 calls per timed sample - testing
    # whether noise keeps dropping with more iterations or has already
    # flattened out by iterations=30.
    benchmark.extra_info["n"] = MEMCOPY_OPTIMIZED_N
    result = benchmark.pedantic(memcopy_anchor_optimized, iterations=100, rounds=10)

    assert result.shape == (MEMCOPY_OPTIMIZED_N,)

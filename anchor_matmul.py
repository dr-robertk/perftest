"""Compute-bound anchor benchmark: dense matrix multiplication.

Run alongside the main solveDirichletNeumann benchmarks (same CI job, same
instance) so its timing can be used to normalize hardware/co-tenancy noise
out of the main results - see the thesis goal document's "reference or
calibration benchmarks executed alongside the target benchmark" approach.

FLOP-heavy and vectorizes/parallelizes well via BLAS, in contrast with
anchor_memcopy's memory-bandwidth-bound profile. Fixed seed so every call
multiplies the exact same matrices, isolating hardware/environment effects
from any data-dependent variation.
"""

import numpy as np


def matmul_anchor(n: int = 5120) -> np.ndarray:
    rng = np.random.default_rng(seed=0)
    a = rng.random((n, n))
    b = rng.random((n, n))
    return a @ b

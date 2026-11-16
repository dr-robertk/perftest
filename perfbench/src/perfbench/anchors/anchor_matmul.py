"""Compute-bound anchor benchmark using dense matrix multiplication."""

import numpy as np


def matmul_anchor(n: int = 5120) -> np.ndarray:
    rng = np.random.default_rng(seed=0)
    a = rng.random((n, n))
    b = rng.random((n, n))
    return a @ b

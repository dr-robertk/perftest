"""Memory-bandwidth-bound anchor benchmark: STREAM-style vector triad.

Run alongside the main solveDirichletNeumann benchmarks (same CI job, same
instance) so its timing can be used to normalize hardware/co-tenancy noise
out of the main results - see the thesis goal document's "reference or
calibration benchmarks executed alongside the target benchmark" approach.

Computes a[i] = b[i] + scalar * c[i] (the classic STREAM "triad" kernel):
one multiply and one add per three array accesses, so runtime is dominated
by memory bandwidth rather than compute - in contrast with anchor_matmul's
compute/FLOP-bound profile. Fixed seed so every call operates on the exact
same arrays, isolating hardware/environment effects from any data-dependent
variation.
"""

import numpy as np


def memcopy_anchor(n: int = 80_000_000) -> np.ndarray:
    rng = np.random.default_rng(seed=0)
    b = rng.random(n)
    c = rng.random(n)
    scalar = 3.0
    return b + scalar * c

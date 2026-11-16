"""Memory-bandwidth-bound anchor benchmark using a STREAM-style vector triad."""

import numpy as np


def memcopy_anchor(n: int = 80_000_000) -> np.ndarray:
    rng = np.random.default_rng(seed=0)
    b = rng.random(n)
    c = rng.random(n)
    return b + 3.0 * c

import numpy as np
from room import Boundary, Room

# Tunable parameters
WALL = 15
HEATER = 40
WINDOW = 5
W = 0.8
ITERATIONS = 10

# Default grid resolution along room 1/room 3's shared edge.
# Room 2 is twice as tall (2 * N), room 1 and room 3 are square (N x N).
N = 101


def step_size(n: int) -> float:
    return 1 / (n - 1)


def gamma1(n: int):
    return Boundary(WALL * np.ones(n), np.array([1] + [0] * (n - 2) + [1]))


def gamma2(n: int):
    return Boundary(WALL * np.ones(n), np.array([1] + [0] * (n - 2) + [1]))


def omega1(n: int = N) -> Room:
    lb1 = Boundary(HEATER * np.ones(n), np.ones(n))
    tb1 = Boundary(WALL * np.ones(n), np.ones(n))
    rb1 = gamma1(n)
    bb1 = Boundary(WALL * np.ones(n), np.ones(n))
    return Room(lb1, tb1, rb1, bb1)


def omega2(n: int = N) -> Room:
    y_n_2 = 2 * n
    g1 = gamma1(n)
    g2 = gamma2(n)
    lb2 = g1 + Boundary(
        WALL * np.ones(y_n_2 - g1.values.shape[0]),
        np.ones(y_n_2 - g1.values.shape[0]),
    )
    tb2 = Boundary(HEATER * np.ones(n), np.ones(n))
    rb2 = Boundary(WALL * np.ones(y_n_2 - len(g2)), np.ones(y_n_2 - len(g2))) + g2
    bb2 = Boundary(WINDOW * np.ones(n), np.ones(n))
    return Room(lb2, tb2, rb2, bb2)


def omega3(n: int = N) -> Room:
    lb3 = gamma2(n)
    tb3 = Boundary(WALL * np.ones(n), np.ones(n))
    rb3 = Boundary(HEATER * np.ones(n), np.ones(n))
    bb3 = Boundary(WALL * np.ones(n), np.ones(n))
    return Room(lb3, tb3, rb3, bb3)

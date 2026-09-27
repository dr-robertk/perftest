import numpy as np
from room import Boundary, Room

# Tunable parameters
WALL = 15
HEATER = 40
WINDOW = 5
W = 0.8
ITERATIONS = 10

# Describing room 1
X_N_1 = 101
Y_N_1 = X_N_1
# Describing room 2
X_N_2 = X_N_1
Y_N_2 = 2 * X_N_2
# Describing room 3
X_N_3 = X_N_1
Y_N_3 = Y_N_1

# The
H = 1 / (X_N_1 - 1)


def gamma1():
    return Boundary(WALL * np.ones(Y_N_1), np.array([1] + [0] * (Y_N_1 - 2) + [1]))


def gamma2():
    return Boundary(WALL * np.ones(Y_N_3), np.array([1] + [0] * (Y_N_3 - 2) + [1]))


def omega1() -> Room:
    lb1 = Boundary(HEATER * np.ones(Y_N_1), np.ones(Y_N_1))
    tb1 = Boundary(WALL * np.ones(X_N_1), np.ones(X_N_1))
    rb1 = gamma1()
    bb1 = Boundary(WALL * np.ones(X_N_1), np.ones(X_N_1))
    return Room(lb1, tb1, rb1, bb1)


def omega2() -> Room:
    g1 = gamma1()
    g2 = gamma2()
    lb2 = g1 + Boundary(
        WALL * np.ones(Y_N_2 - g1.values.shape[0]),
        np.ones(Y_N_2 - g1.values.shape[0]),
    )
    tb2 = Boundary(HEATER * np.ones(X_N_2), np.ones(X_N_2))
    rb2 = Boundary(WALL * np.ones(Y_N_2 - len(g2)), np.ones(Y_N_2 - len(g2))) + g2
    bb2 = Boundary(WINDOW * np.ones(X_N_2), np.ones(X_N_2))
    return Room(lb2, tb2, rb2, bb2)


def omega3() -> Room:
    lb3 = gamma2()
    tb3 = Boundary(WALL * np.ones(X_N_3), np.ones(X_N_3))
    rb3 = Boundary(HEATER * np.ones(Y_N_3), np.ones(Y_N_3))
    bb3 = Boundary(WALL * np.ones(X_N_3), np.ones(X_N_3))
    return Room(lb3, tb3, rb3, bb3)

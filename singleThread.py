import numpy as np

from config import ITERATIONS, H, W, omega1, omega2, omega3

# from room import plot_temp_rooms


def solveDirichletNeumann():

    o1 = omega1()
    o2 = omega2()
    o3 = omega3()

    ########################### Dirchlet Neumann iterations ###########################
    t1s = []
    t2s = []
    t3s = []
    for i in range(ITERATIONS):
        t2, *_ = o2.solveDirichlet()
        left, _, right, _ = o2.neumannValues(t2, H)

        idx12 = o1.right.dirichlet == 0
        idx21 = o2.left.dirichlet == 0
        idx23 = o2.right.dirichlet == 0
        idx32 = o3.left.dirichlet == 0

        o1.right.values[idx12] = left.values[idx21]
        t1, *_ = o1.solveNeumann()
        o2.left.values[idx21] = t1[idx12, -1]

        o3.left.values[idx32] = right.values[idx23]
        t3, *_ = o3.solveNeumann()
        o2.right.values[idx23] = t3[idx32, 0]

        if i != 0:
            t1 = W * t1 + (1 - W) * t1s[-1]
            t2 = W * t2 + (1 - W) * t2s[-1]
            t3 = W * t3 + (1 - W) * t3s[-1]
        t1s.append(t1)
        t2s.append(t2)
        t3s.append(t3)

    np.set_printoptions(precision=0)
    print("\n", "=" * 38, " Ω1 ", "=" * 38)
    print(t1)
    print("\n", "=" * 38, " Ω2 ", "=" * 38)
    print(t2)
    print("\n", "=" * 38, " Ω3 ", "=" * 38)
    print(t3)
    return t1, t2, t3
    # plot_temp_rooms([t1, t2, t3])

if __name__ == "__main__":
    solveDirichletNeumann()

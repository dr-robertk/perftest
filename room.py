from dataclasses import dataclass
from pprint import pprint

# import matplotlib.pyplot as plt
import numpy as np
from config import *
from scipy.sparse import diags, linalg


@dataclass
class Boundary:
    """Describes a boundary of a room.
    Args:
        values (np.ndarray): The values along the border
        dirichlet (np.ndarray): Mask indicating dirichlet or Neumann condition
    """

    values: np.ndarray
    dirichlet: np.ndarray

    def __add__(self, other):
        return Boundary(
            np.concatenate((self.values, other.values)),
            np.concatenate((self.dirichlet, other.dirichlet)),
        )

    def __len__(self):
        return self.values.shape[0]


@dataclass
class Room:
    """
    Describes a room.

    Args:
        left (Boundary): The left boundry
        top (Boundary): The top boundry
        right (Boundary): The right boundry
        bottom (Boundary): The bottom boundry
    """

    left: Boundary
    top: Boundary
    right: Boundary
    bottom: Boundary

    @property
    def xN(self):
        """Number of points along the x-axis"""
        return self.top.values.shape[0]

    @property
    def yN(self):
        """Number of points along the y-axis"""
        return self.left.values.shape[0]

    @property
    def N(self):
        """Total number of points in the room"""
        return self.xN * self.yN

    def neumannValues(self, temperature: np.ndarray, h):
        """Calculate neumann values for all boundries

        Args:
            temperature (np.ndarray): Temperature matrix
            h (float): stepsize

        Returns:
            (left, top, right, bottom) neumann values
        """
        left = Boundary(np.zeros(len(self.left)), self.left.dirichlet)
        right = Boundary(np.zeros(len(self.right)), self.right.dirichlet)
        for i, (l, r) in enumerate(zip(self.left.dirichlet, self.right.dirichlet)):
            if l == 0:
                left.values[i] = h * (
                    -3 * temperature[i, 0]
                    + temperature[i + 1, 0]
                    + temperature[i - 1, 0]
                    + temperature[i, 1]
                )
            if r == 0:
                right.values[i] = h * (
                    -3 * temperature[i, -1]
                    + temperature[i + 1, -1]
                    + temperature[i - 1, -1]
                    + temperature[i, -2]
                )

        top = Boundary(np.zeros(len(self.top)), self.top.dirichlet)
        bottom = Boundary(np.zeros(len(self.bottom)), self.bottom.dirichlet)
        for i, (t, b) in enumerate(zip(self.top.dirichlet, self.bottom.dirichlet)):
            if t == 0:
                top.values[i] = h * (
                    -3 * temperature[-1, i]
                    + temperature[-1, i + 1]
                    + temperature[-1, i - 1]
                    + temperature[-2, i]
                )
            if b == 0:
                bottom.values[i] = h * (
                    -3 * temperature[0, i]
                    + temperature[0, i + 1]
                    + temperature[0, i - 1]
                    + temperature[1, i]
                )
        return left, top, right, bottom

    def _getSystem(self, format="csr"):
        """Generate dirchlet system

        Args:
            format (str, optional): sparse array format. Defaults to "csc".

        Returns:
            A, b: Matrix and boundry array
        """
        d0 = np.ones(self.N)
        d1 = np.zeros(self.N - 1)
        d2 = np.zeros(self.N - self.yN)

        for i in range(1, self.xN - 1):
            d0[i * self.yN + 1 : (i + 1) * self.yN - 1] = -4
            d1[i * self.yN + 1 : (i + 1) * self.yN - 1] = 1
            d2[i * self.yN + 1 : (i + 1) * self.yN - 1] = 1

        b = np.zeros(self.N)
        b[: self.yN] = self.left.values
        b[-self.yN :] = self.right.values
        b[:: self.yN] = self.bottom.values
        b[self.yN - 1 :: self.yN] = self.top.values

        A = diags(
            [np.flip(d2), np.flip(d1), d0, d1, d2],
            [-self.yN, -1, 0, 1, self.yN],
            format=format,
        )

        return A, b

    def solveNeumann(self):
        """Solve Neumann system. Assumes the neumann values are put in the boundry

        Returns:
            T, A, b: solution and the system
        """
        A, b = self._getSystem("lil")
        for i in range(self.yN):
            l_idx = i
            r_idx = i - self.yN
            if self.left.dirichlet[i] == 0:
                A[l_idx, l_idx] = -3
                A[l_idx, l_idx + 1] = 1
                A[l_idx, l_idx - 1] = 1
                A[l_idx, l_idx + self.yN] = 1

            if self.right.dirichlet[i] == 0:
                A[r_idx, r_idx] = -3
                A[r_idx, r_idx + 1] = 1
                A[r_idx, r_idx - 1] = 1
                A[r_idx, r_idx - self.yN] = 1

        # TODO: implement for top and bottom

        return linalg.spsolve(A.tocsr(), b).reshape(self.yN, self.xN, order="F"), A, b

    def solveDirichlet(self):
        """Solve Dirichlet system

        Returns:
            T, A, b: solution and the system
        """
        A, b = self._getSystem()
        return linalg.spsolve(A, b).reshape(self.yN, self.xN, order="F"), A, b


# def plot_temp(temps):
#     """Plot temperature matrices"""
#     for i, temp in enumerate(temps):
#         plt.figure(i)
#         y_N, x_N = temp.shape
#         X, Y = np.meshgrid(
#             np.linspace(0, 1, x_N), np.linspace(0, 1.0 * (y_N) / (x_N), y_N)
#         )
#         plt.title("Temperature in the room")
#         plt.contourf(X, Y, temp, levels=500, cmap=plt.cm.coolwarm, vmin=5, vmax=40)
#         plt.colorbar()

#     plt.show()


# def plot_temp_rooms(temps):
#     """Plot all rooms in one plot"""
#     for i, T in enumerate(temps):
#         print(T.shape)
#         print("hello")
#         t1, t2, t3 = T

#         plt.figure(i)
#         xn = t1.shape[1]
#         yn = t1.shape[0]
#         t = np.nan * np.zeros((2 * xn, 3 * yn))
#         t[0:xn, 0:yn] = t1
#         t[0 : 2 * xn, yn : 2 * yn] = t2
#         t[xn : 2 * xn, 2 * yn : 3 * yn] = t3
#         X, Y = np.meshgrid(
#             np.linspace(0, 1, t.shape[1]), np.linspace(0, 1.0, t.shape[0])
#         )
#         plt.title("Temperature in the room")
#         plt.contourf(X, Y, t, levels=500, cmap=plt.cm.coolwarm, vmin=5, vmax=40)
#         plt.colorbar()

#     plt.show()

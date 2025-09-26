from functools import lru_cache
from math import floor, pi

import matplotlib.pyplot as plt
import numpy as np

import manim_lamination_builder as lb


# take the function described now in case 1 a=2 of the restricted to homomorphism statement.
def sigma(x, d):
    return d * x % 1


x = np.linspace(0, 1, 1000)  # 400 points from 0 to 1
x = x[0:-1]


def digit_for_phi(x, JLeftEnd, d):
    assert JLeftEnd * d + 1 <= d
    if x <= JLeftEnd:
        return floor(x * d) % (d - 1)
    if x >= JLeftEnd + 1 / d:
        return (floor(x * d) - 1) % (d - 1)
    return None


@lru_cache(maxsize=None)  # maxsize=None means unlimited cache size
def image_of_b(a, d) -> float:
    iterate = a
    digits = []
    for _ in range(1000):
        digit = digit_for_phi(iterate, a, d)
        if digit is None:
            return lb.NaryFraction(
                exact=(), repeating=tuple(digits), degree=d - 1
            ).to_float()
        digits.append(digit)
        iterate = sigma(iterate, d)

    return lb.NaryFraction(exact=tuple(digits), repeating=(), degree=d - 1).to_float()


def phi(x, JLeftEnd: float, d):
    added_stuff = image_of_b(JLeftEnd, d)
    sum = 0
    iterate = x
    for i in range(1000):
        digit = digit_for_phi(iterate, JLeftEnd, d)
        if digit is None:
            return sum + added_stuff / (d - 1) ** (i)
        sum += digit / (d - 1) ** (i + 1)
        iterate = sigma(iterate, d)
    return sum


d = 3


def graph_phi(a):
    y = [phi(x, a, d) for x in x]
    plt.plot(x, y, label="phi(x)")
    plt.xlabel("x")
    plt.ylabel("phi(x)")
    plt.title("Graph of phi(x) a = {}".format(a))
    plt.legend()
    plt.grid(True)
    plt.show()


def test_semi_conjigacy(a):
    plt.plot(x, [phi(sigma(x, d), a, d) for x in x], label="phi(sigma_d(x))")
    plt.plot(x, [sigma(phi(x, a, d), d) for x in x], label="sigma_{d-1}(phi(x))")
    plt.xlabel("x")
    plt.ylabel("phi(x)")
    plt.title("Semi-Conjigate?")
    plt.legend()
    plt.grid(True)
    plt.show()


def compair(a1, a2):
    y = [phi(x, a1, d) for x in x]
    plt.plot(x, y, label="JLeftEnd={}".format(a1))
    y = [phi(x, a2, d) for x in x]
    plt.plot(x, y, label="JLeftEnd={}".format(a2))
    plt.xlabel("x")
    plt.ylabel("phi(x)")
    plt.title("Graph of phi(x)")
    plt.legend()
    plt.grid(True)
    plt.show()


# import random
#
# for i in range(100):
#     compair(random.random() * 0.75, random.random() * 0.75)


# Make a grid; choose resolution as desired
def graph2d():
    n_x = 1000
    n_y = 1000
    x_vals = np.linspace(0, 1, n_x)[:-1]
    y_vals = np.linspace(0, 0.75, n_y)[:-1]

    # Evaluate function on the grid using iteration
    Z = []
    for y in y_vals:
        row = []
        for x in x_vals:
            row.append(phi(x, y, d))
        Z.append(row)

    # Convert to NumPy arrays for plotting
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.array(Z)

    # Plotting
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap="flag")
    fig.colorbar(surf)
    ax.set_xlabel("x")
    ax.set_ylabel("a")
    ax.set_zlabel("phi(x)")
    # plt.title("Surface plot of function over [0,1] x [0,0.75]")
    plt.show()


# graph2d()


def psi(x, a, destination_degree, lesser=True):
    d = destination_degree
    iterate = x
    old_digits = lb.NaryFraction.from_float(x, d - 1).exact
    digits = []
    for i, xi in enumerate(old_digits):
        # print(iterate)
        criteria = None
        if lesser:
            criteria = iterate <= a
        else:
            criteria = iterate < a
        if criteria:
            digits.append(xi)
        else:
            digits.append(xi + 1)
        iterate = sigma(iterate, d - 1)
    return lb.NaryFraction(exact=tuple(digits), repeating=(), degree=d).to_float()


def graph_psi(a, lesser):
    x = np.linspace(0, 1, 1000)  # 400 points from 0 to 1
    x = x[0:-1]
    y = [psi(x, a, d, lesser=lesser) for x in x]
    pos = np.where(np.abs(np.diff(y)) >= 0.01)[0] + 1
    x = np.insert(x, pos, np.nan)
    y = np.insert(y, pos, np.nan)
    plt.plot(x, y)
    plt.xlim(-0.005, 1.005)
    plt.ylim(-0.005, 1.005)
    plt.xlabel("x")
    # plt.ylabel("psi(x)")
    plt.title("Graph of psi^{}(x) a = {}".format("-" if lesser else "+", a))
    plt.legend()
    plt.grid(True)
    plt.show()


# print(psi(0.5, 7.5))


def test_semi_conjigacy_psi(a):
    plt.plot(x, [psi(sigma(x, d - 1), a, d) for x in x], label="psi(sigma_{d-1}(x))")
    plt.plot(x, [sigma(psi(x, a, d), d) for x in x], label="sigma_d(psi(x))")
    plt.xlabel("x")
    plt.title("Semi-Conjigate?")
    plt.legend()
    plt.grid(True)
    plt.show()


# import random
#
# for i in range(100):
#     test_semi_conjigacy_psi(random.random())

# print(psi(1 / 3, 1 / 4))


def test_left_inverse(a):
    b = psi(a, a, d, lesser=True)
    # plt.plot(x, , label="psi(sigma_3(x))")
    plt.plot(x, [phi(psi(x, a, d), b, d) for x in x], label="phi_b(psi_a(x))")
    plt.xlabel("x")
    plt.title("Left Inverse? b=psi_a(a)")
    plt.legend()
    plt.grid(True)
    plt.show()


# import random
#
# for i in range(5):
#     test_left_inverse(random.random())


def graph_psi_diagonal():
    plt.plot(x, [psi(x, x, d) for x in x], label="psi_x(x)")
    plt.xlabel("x")
    plt.title("Monotone Diagonal?")
    plt.legend()
    plt.grid(True)
    plt.show()


# graph_psi_diagonal()
# test_left_inverse(pi % 1)

# for M_2 in [lb.NaryFraction.from_string(2, "_0")]:
#     # M_2 becomes the major under \Psi
#     siblings = M_2.siblings()
#     sibling = M_2.siblings()[siblings[0] == M_2]
#     print(psi(sibling.to_float(), M_2.to_float(), 3, lesser=False))
#

# graph_psi(0, lesser=True)
# graph_psi(0, lesser=False)
# graph_psi(1 / 12)
# graph_phi(1 / 8)
# graph_phi(1 / 3)
# print(psi(0, 0, 3, lesser=True))
# print(psi(0, 0, 3, lesser=False))

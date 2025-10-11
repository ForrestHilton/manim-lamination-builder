import itertools
import random
from math import gcd

from manim_lamination_builder import Orbit, sigma


def test_deployment_sequence():
    assert Orbit([3], [1, 3]).getSpacialOrbit()[0].to_string() == "_001"
    assert Orbit([2, 3], [1, 3]).getSpacialOrbit()[0].to_string() == "_002"
    assert Orbit([1, 3], [1, 3]).getSpacialOrbit()[0].to_string() == "_012"


def test_rotation_number():
    assert Orbit([2, 3], [1, 3]).getSpacialOrbit()[0].to_string() == "_002"
    assert Orbit([2, 3], [2, 3]).getSpacialOrbit()[0].to_string() == "_021"


def test_composite_rotation_number():
    assert Orbit([2, 4], [2, 4]).getSpacialOrbit()[0].to_string() == "_02"
    assert Orbit([4, 4], [2, 4]).getSpacialOrbit()[0].to_string() == "_01"


def random_partition(total, slots):
    # Pick slots-1 cut-points in 0..total (inclusive), sort, and use differences
    cuts = sorted([0] + [random.randint(0, total) for _ in range(slots - 1)] + [total])
    return [cuts[i + 1] - cuts[i] for i in range(slots)]


def test_goldberg_random_is_correct():
    for den in range(1, 5):
        for num in range(1, den):
            if gcd(num, den) != 1:
                break
            for d in range(2, 4):
                rand_list = random_partition(den, d - 1)
                deployment = list(itertools.accumulate(rand_list))
                point = Orbit(deployment, [num, den]).getSpacialOrbit()[0]
                pair = "goldbergOrbit({},[{},{}]) -> {}".format(
                    deployment, num, den, point
                )
                iterate = point
                orbit = []
                for _ in range(len(point.repeating)):
                    orbit.append(iterate.to_float())
                    iterate = sigma(iterate)
                for i, quota in enumerate(deployment):
                    assert (
                        len([x for x in orbit if x < (i + 1) / (d - 1)]) == quota
                    ), "goldbergOrbit does not match the deployment sequence: {}".format(
                        pair
                    )


# TODO: Should the goldberg orbit return the least moment of the orbit?
# TODO: can the test above test if the rotation number is respected?
# TODO: can the test above be extended for gcd != 1
# TODO: Should orbits.py use the python convention for variable names?

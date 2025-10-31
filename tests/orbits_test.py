import itertools
import random
from math import gcd

from manim_lamination_builder import PeriodicOrbit, sigma
from manim_lamination_builder.points import NaryFraction


def test_deployment_sequence():
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([3], [1, 3]).spacial_orbit[0].to_string()
        == "_001"
    )
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([2, 3], [1, 3])
        .spacial_orbit[0]
        .to_string()
        == "_002"
    )
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([1, 3], [1, 3])
        .spacial_orbit[0]
        .to_string()
        == "_012"
    )


def test_rotation_number():
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([2, 3], [1, 3])
        .spacial_orbit[0]
        .to_string()
        == "_002"
    )
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([2, 3], [2, 3])
        .spacial_orbit[0]
        .to_string()
        == "_021"
    )


def test_composite_rotation_number():
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([2, 4], [2, 4])
        .spacial_orbit[0]
        .to_string()
        == "_02"
    )
    assert (
        PeriodicOrbit.from_dep_seq_and_rot_num([4, 4], [2, 4])
        .spacial_orbit[0]
        .to_string()
        == "_01"
    )


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
                point = PeriodicOrbit.from_dep_seq_and_rot_num(
                    deployment, [num, den]
                ).spacial_orbit[0]
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

    def test_goldberg_random_is_correct():
        for den in range(1, 5):
            for num in range(1, den):
                if gcd(num, den) != 1:
                    break
                for d in range(2, 4):
                    rand_list = random_partition(den, d - 1)
                    deployment = list(itertools.accumulate(rand_list))


# TODO: Should the goldberg orbit return the least moment of the orbit?
# TODO: can the test above test if the rotation number is respected?
# TODO: can the test above be extended for gcd != 1


def test_orbits_zero():
    assert len(PeriodicOrbit(NaryFraction.from_string(2, "0")).spacial_orbit) == 1

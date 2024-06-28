"""
Most of the tests here were needed to diagnose an issue that is no longer present in the code.
"""

from manim.animation.animation import config
from manim.utils.file_ops import config
from manim_lamination_builder import parse_lamination
from manim_lamination_builder import TreeRender, next_pull_back, PullBackTree
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.constructions import fussCatalan, pollygons_are_one_to_one
from manim_lamination_builder.custom_json import custom_dump, custom_parse
from manim_lamination_builder.lamination import LeafLamination
from manim_lamination_builder.main import Main
from manim_lamination_builder import FloatWrapper, NaryFraction, sigma
from manim_lamination_builder.new_generate import (
    _sibling_collections_of_leaf_in_existing,
    _sibling_collections_of_leaf,
    pre_image_dictionary,
)

import random


def test_chord_works_as_expected():
    a1 = NaryFraction.from_string(2, "00_100")
    a2 = NaryFraction.from_string(2, "0_010")
    b1 = NaryFraction.from_string(2, "_101")
    b2 = NaryFraction.from_string(2, "1_011")
    assert a1 == a2
    assert b1 == b2
    assert Chord(a1, b1) == Chord(a2, b2)
    assert Chord(a1, b1) in [Chord(a2, b2)]


def test_issolated_collections():
    for d in range(2, 8):
        num1 = random.random()
        num2 = random.random()

        while num1 == num2:
            num2 = random.random()

        l = Chord(FloatWrapper(num1, d), FloatWrapper(num2, d))
        actuall = []
        for c in _sibling_collections_of_leaf(l):
            actuall.append(frozenset(c))
            for lp in c:
                assert sigma(lp) == l
        assert len(actuall) == fussCatalan(d, 2)
        assert l == Chord(FloatWrapper(num1, d), FloatWrapper(num2, d))


# test_issolated_collections()


def test_issolated_collections2():
    l = Chord(
        NaryFraction.from_string(2, "0_010"), NaryFraction.from_string(2, "0_100")
    )
    # at this point, I fixed l.min.pre_images()
    actuall = []
    for c in _sibling_collections_of_leaf(l):
        actuall.append(frozenset(c))
        for lp in c:
            assert sigma(lp) == l
    assert len(actuall) == 2


def test_preimage_dictionary():
    start = parse_lamination("""
{"leafs": [["1_010", "1_100"], ["0_010", "0_100"], ["0_001", "1_010"], ["0_010", "1_001"], ["0_001", "1_100"], ["0_100", "1_001"]], "points": [], "degree": 2}
            """)
    dict = pre_image_dictionary(start)
    hist = [0, 0, 0]
    for l, v in dict.items():
        hist[len(v)] += 1
        for lp in v:
            assert sigma(lp) == l
    assert hist == [0, 0, 3]


def test_single_leavs1():
    l = Chord(
        NaryFraction.from_string(2, "1_010"), NaryFraction.from_string(2, "1_100")
    )
    L = custom_parse('{"leafs": [], "points": [], "degree": 2}')
    required = custom_parse("[]")

    result = _sibling_collections_of_leaf_in_existing(l, L, required)
    assert len(result) == 2


def test_single_leavs2():
    start = parse_lamination("""
{"leafs": [["1_010", "1_100"], ["0_010", "0_100"], ["0_001", "1_010"], ["0_010", "1_001"], ["0_001", "1_100"], ["0_100", "1_001"]], "points": [], "degree": 2}
            """)
    existing_pre_images = pre_image_dictionary(start)

    l = Chord(
        NaryFraction.from_string(2, "0_010"), NaryFraction.from_string(2, "0_100")
    )
    required = existing_pre_images.get(l, [])

    L = custom_parse(
        '[{"leafs": [["11_010", "11_100"], ["01_010", "01_100"]], "points": [],'
        ' "degree": 2}, {"leafs": [["01_100", "11_010"], ["01_010", "11_100"]],'
        ' "points": [], "degree": 2}]'
    )

    assert all([sigma(l2) == l for l2 in required])
    assert len(required) == 2
    result = _sibling_collections_of_leaf_in_existing(l, L[0], required)

    assert len(result) == 1


def test_new_sibling_portraits():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:3}"""
    ).to_leafs()
    portraits = next_pull_back(start)
    assert len(portraits) == 4

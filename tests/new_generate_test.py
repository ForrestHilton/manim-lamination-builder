from manim.animation.animation import config
from manim.utils.file_ops import config
from manim_lamination_builder import parse_lamination
from manim_lamination_builder import TreeRender, next_pull_back, PullBackTree
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.constructions import fussCatalan
from manim_lamination_builder.custom_json import custom_dump, custom_parse
from manim_lamination_builder.main import Main
from manim_lamination_builder.points import FloatWrapper, NaryFraction, sigma
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
        assert len(actuall) == fussCatalan(d, 2)


def test_preimage_dictionary():
    start = parse_lamination(
        """
{"leafs": [["1_010", "1_100"], ["0_010", "0_100"], ["0_001", "1_010"], ["0_010", "1_001"], ["0_001", "1_100"], ["0_100", "1_001"]], "points": [], "radix": 2}
            """
    )
    dict = pre_image_dictionary(start)
    hist = [0,0,0]
    for l, v in dict.items():
        hist[len(v)] += 1
        for lp in v:
            assert Chord(sigma(lp.min), sigma(lp.max)) == l
    assert hist == [0,0,3]


def test_single_leavs1():
    l = Chord(
        NaryFraction.from_string(2, "1_010"), NaryFraction.from_string(2, "1_100")
    )
    L = custom_parse('{"leafs": [], "points": [], "radix": 2}')
    required = custom_parse("[]")

    result = _sibling_collections_of_leaf_in_existing(l, L, required)
    assert len(result) == 2


def test_single_leavs2():
    l = Chord(
        NaryFraction.from_string(2, "0_010"), NaryFraction.from_string(2, "0_100")
    )
    L = custom_parse(
        '{"leafs": [["11_010", "11_100"], ["01_010", "01_100"]], "points": [], "radix": 2}'
    )
    required = custom_parse('[["0_001", "1_010"], ["0_010", "1_001"]]')

    # white box examination shows these as the possible pullbacks of the leaf
    ["0_010", "0_100"]
    ["1_010", "1_100"]

    ["0_010", "1_100"]
    ["0_100", "1_010"]
    result = _sibling_collections_of_leaf_in_existing(l, L, required)

    assert len(result) == 1


def test_new_sibling_portraits():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],radix:3}"""
    ).to_leafs()
    portraits = next_pull_back(start)
    assert len(portraits) == 4


def test_rabbit_tree():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],radix:2}"""
    ).to_leafs()
    tree = PullBackTree(start, 4)
    list_of_lists = tree.flaten()
    assert len(list_of_lists) == 5
    assert len(list_of_lists[0]) == 1
    assert len(list_of_lists[1]) == 1
    assert len(list_of_lists[2]) == 1
    assert len(list_of_lists[3]) == 1
    assert len(list_of_lists[4]) == 4


def show_rabbit_tree():
    config.preview = True
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],radix:2}"""
    ).to_leafs()
    tree = PullBackTree(start, 4)
    TreeRender(tree).render()


if __name__ == "__main__":
    config.preview = True
    test_preimage_dictionary()
    # main = parse_lamination(
    #     '{"leafs": [["11_010", "11_100"], ["01_010", "01_100"]], "points": [], "radix": 2}'
    # )
    # leaf = parse_lamination('{"leafs": [["0_010", "0_100"]], "points": [], "radix": 2}')
    # required = parse_lamination(
    #     '{"leafs": [["0_001", "1_010"], ["0_010", "1_001"]], "points": [], "radix": 2}'
    # )
    # Main([main, leaf, required]).render()

"""
Most of the tests here were needed to diagnose an issue that is no longer present in the code.
"""

from manim.animation.animation import config

from manim_lamination_builder import custom_json

config.preview = True
import random

from manim.utils.file_ops import config

from manim_lamination_builder import (
    FloatWrapper,
    NaryFraction,
    PullBackTree,
    TreeRender,
    next_pull_back,
    parse_lamination,
    sigma,
)
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.constructions import fussCatalan, pollygons_are_one_to_one
from manim_lamination_builder.custom_json import custom_dump, custom_parse
from manim_lamination_builder.lamination import GapLamination, LeafLamination
from manim_lamination_builder.main import Main
from manim_lamination_builder.new_generate import (
    _sibling_collections_of_leaf,
    _sibling_collections_of_leaf_in_existing,
    pre_image_dictionary,
    sibling_portraits,
)


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


def test_sibling_portraits():
    for d in range(2, 4):
        for order in range(2, 5):
            random_set = set()
            # random_set = [i / (5 * d) for i in range(order)]
            while len(random_set) < order:
                random_set.add(random.random() % 1)
            polygon = sorted(random_set)
            polygon = [FloatWrapper(n, d) for n in polygon]
            new_verticies = [p.pre_images() for p in polygon]
            actuall = sibling_portraits(new_verticies)
            for portrait in actuall:
                # test that the polygons have the corect image and their degree's
                # are d in total
                acc = 0
                for poly in portrait.polygons:
                    image = sorted([p.to_float() for p in sigma(poly)])
                    di = len(poly) // order
                    acc += di
                    for i in range(order):
                        assert abs(polygon[i].to_float() - image[i]) < 0.0000001
                assert acc == d

                leafs = portrait.to_leafs()
                if not leafs.unlinked():
                    Main([leafs]).render()
                assert leafs.unlinked()
                assert len(portrait.polygons) == len(leafs.to_polygons().polygons)
            assert len(actuall) == fussCatalan(d, order + 1)


def random_polygons(number, sides) -> GapLamination:
    polygons = [
        [FloatWrapper(random.random() % 1, 2) for _ in range(sides)]
        for _ in range(number)
    ]
    return GapLamination(polygons=polygons, points=[], degree=2)


def test_polygons_unlinked():
    for numpoly in range(2, 5):
        for sides in range(2, 5):
            lam = random_polygons(numpoly, sides)
            assert lam.unlinked() == lam.to_leafs().unlinked()


def test_polygons_coexist():
    a = custom_parse(
        """{"points": [], "degree": 2, "polygons": [[0.05310929458218239, 0.6150710279856368], [0.10922703411711854, 0.8479865926668774]]}"""
    )
    b = custom_parse(
        """{"points": [], "degree": 2, "polygons": [[0.1464253152363102, 0.5207268840907326], [0.1253695002398284, 0.5482237087008556]]}"""
    )
    both = GapLamination(polygons=a.polygons + b.polygons, points=[], degree=2)
    assert both.unlinked() == a.coexists(b)
    for _ in range(10):
        for numpoly in range(2, 4):
            for sides in range(2, 4):
                b = random_polygons(numpoly, sides)
                a = random_polygons(numpoly, sides)
                both = GapLamination(
                    polygons=a.polygons + b.polygons, points=[], degree=2
                )
                assert both.unlinked() == a.coexists(b), "fails for {},{}".format(
                    custom_dump(a), custom_dump(b)
                )


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


# test_issolated_collections2()


def test_preimage_dictionary():
    start = parse_lamination(
        """
{"leafs": [["1_010", "1_100"], ["0_010", "0_100"], ["0_001", "1_010"], ["0_010", "1_001"], ["0_001", "1_100"], ["0_100", "1_001"]], "points": [], "degree": 2}
            """
    )
    dict = pre_image_dictionary(start.to_polygons())
    hist = [0, 0, 0]
    for poly, v in dict.items():
        hist[len(v)] += 1
        for image_poly in v:
            assert sigma(image_poly) == poly
    assert hist == [0, 0, 1]


def test_new_sibling_portraits():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:3}"""
    ).to_polygons()
    portraits = next_pull_back(start)
    assert len(portraits) == 4


test_preimage_dictionary()

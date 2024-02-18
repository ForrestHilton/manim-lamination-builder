"""
Most of the tests here were needed to diagnose an issue that is no longer present in the code.
"""

from manim.animation.animation import config
from manim.utils.file_ops import config
from manim_lamination_builder import parse_lamination
from manim_lamination_builder import TreeRender, PullBackTree
from manim_lamination_builder.constructions import pollygons_are_one_to_one
from manim_lamination_builder.custom_json import custom_dump, custom_parse
import networkx as nx


def test_rabbit_tree():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    tree = PullBackTree.build(start, 4)
    list_of_lists = tree.flaten()
    assert len(list_of_lists) == 5
    assert len(list_of_lists[0]) == 1
    assert len(list_of_lists[1]) == 1
    assert len(list_of_lists[2]) == 1
    assert len(list_of_lists[3]) == 1
    assert len(list_of_lists[4]) == 4


def test_restore_rabbit_tree():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    tree = custom_parse(custom_dump(PullBackTree.build(start, 4)))
    assert isinstance(tree, PullBackTree)
    list_of_lists = tree.flaten()
    assert len(list_of_lists) == 5
    assert len(list_of_lists[0]) == 1
    assert len(list_of_lists[1]) == 1
    assert len(list_of_lists[2]) == 1
    assert len(list_of_lists[3]) == 1
    assert len(list_of_lists[4]) == 4


def test_rabbit_tree_one_to_one():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    tree = PullBackTree.build(start, 4)
    options = tree.flaten()[4]
    for o in [options[0], options[2], options[3]]:
        assert len(o.to_polygons().polygons) == 16
        assert pollygons_are_one_to_one(o)

    assert len(options[1].to_polygons().polygons) == 15
    assert not pollygons_are_one_to_one(options[1])


def show_rabbit_tree():
    config.preview = True
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    tree = PullBackTree.build(start, 4)
    TreeRender(tree).render()


def test_nxtree():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    tree = PullBackTree.build(start, 4)
    (G, table) = tree.nx_tree()
    assert nx.to_nested_tuple(G.to_undirected(), 0) == (((((), (), (), ()),),),)
    


# test_nxtree()
# if True:
if __name__ == "__main__":
    # show_rabbit_tree()
    config.preview = True
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    # for steps, list_at_level in enumerate(tree.flaten()):
    #     print(len(list_at_level))
    # for steps, list_at_level in enumerate(tree.flaten()):
    #     condensed = [L.to_polygons() for L in list_at_level]
    #     print(custom_dump(condensed))

    # TreeRender(tree).render()
    # for steps, list_at_level in enumerate(tree.flaten()):
    #     print(len(list_at_level))

    # main = parse_lamination(
    #     '{"leafs": [["11_010", "11_100"], ["01_010", "01_100"]], "points": [], "degree": 2}'
    # )
    # leaf = parse_lamination('{"leafs": [["0_010", "0_100"]], "points": [], "degree": 2}')
    # required = parse_lamination(
    #     '{"leafs": [["0_001", "1_010"], ["0_010", "1_001"]], "points": [], "degree": 2}'
    # )

    # Main(tree.flaten()[-1]).render()

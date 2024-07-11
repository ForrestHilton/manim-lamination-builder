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
    list_of_lists = tree.flatten()
    assert len(list_of_lists) == 5
    assert len(list_of_lists[0]) == 1
    assert len(list_of_lists[1]) == 1
    assert len(list_of_lists[2]) == 1
    assert len(list_of_lists[3]) == 1
    assert len(list_of_lists[4]) == 4


def test_rabbit_tree_extend():
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()
    tree = PullBackTree.build(start, 3)
    tree = tree.extend_by_one_level()
    list_of_lists = tree.flatten()
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
    list_of_lists = tree.flatten()
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
    options = tree.flatten()[4]
    for o in options:
        if pollygons_are_one_to_one(o):
            assert len(o.to_polygons().polygons) == 16
        else:
            assert len(o.to_polygons().polygons) == 15


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


if __name__ == "__main__":
    config.preview = True
    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],degree:2}"""
    ).to_leafs()

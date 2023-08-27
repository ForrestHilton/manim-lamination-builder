from manim.animation.animation import config
from manim.utils.file_ops import config
from manim_lamination_builder import parse_lamination
from manim_lamination_builder import TreeRender, next_pull_back,PullBackTree


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
    assert len(list_of_lists[0]) == 1
    assert len(list_of_lists[1]) == 1
    assert len(list_of_lists[2]) == 1
    assert len(list_of_lists[3]) == 1
    assert len(list_of_lists[4]) == 4
    assert len(list_of_lists) == 5

    
if __name__ == "__main__":
    config.preview = True

    start = parse_lamination(
        """{polygons:[['_100','_010','_001']],radix:2}"""
    ).to_leafs()
    tree = PullBackTree(start, 4)
    TreeRender(tree).render()

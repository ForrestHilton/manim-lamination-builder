from manim_lamination_builder import (
    Angle,
    CriticalTree,
    Main,
    NaryFraction,
    custom_dump,
    parse_lamination,
)


def tree():
    subtree = CriticalTree(
        first_ccw_end_point=NaryFraction.from_string(4, "_1"),
        first_end_point_on_inside=False,
        inside=CriticalTree(
            first_ccw_end_point=NaryFraction.from_string(4, "2_0"),
            first_end_point_on_inside=False,
        ),
    )

    tree = CriticalTree(
        first_ccw_end_point=NaryFraction.from_string(4, "_0"),
        first_end_point_on_inside=False,
        outside=subtree,
    )
    return tree


def test_basic():
    identifyer = tree().is_in_top_branch
    assert 1 == sum(
        [identifyer(y) for y in NaryFraction.from_string(4, "_1").pre_images()]
    )


def test_basic2():
    identifyer = tree().outside.is_in_top_branch
    assert 1 == sum(
        [identifyer(y) for y in NaryFraction.from_string(4, "_1").pre_images()]
    )


def test_basic3():
    print(tree().depth_first_traversal())
    identifyer = tree().depth_first_traversal()[2].is_in_top_branch
    assert 1 == sum(
        [identifyer(y) for y in NaryFraction.from_string(4, "_1").pre_images()]
    )


def test_main():
    for i, identifyer in enumerate(tree().all_branches_identifyers()):
        assert 1 == sum(
            [identifyer(y) for y in NaryFraction.from_string(4, "_1").pre_images()]
        )


if __name__ == "__main__":
    print(custom_dump(tree().as_lamintion()))
    test_main()

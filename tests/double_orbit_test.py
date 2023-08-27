from manim_lamination_builder import double_orbit


def basic_test():
    assert len(double_orbit.polygons) == 1
    assert len(double_orbit.polygons[0]) == 6


if __name__ == "__main__":
    from manim_lamination_builder import Main
    from manim_lamination_builder.main import config

    config.preview = True
    Main([double_orbit]).render()

from manim_lamination_builder import double_orbit
from manim_lamination_builder.animation import AnimateLamination, SigmaAnimation
from manim_lamination_builder.custom_json import custom_dump


def basic_test():
    assert len(double_orbit.polygons) == 1
    assert len(double_orbit.polygons[0]) == 6


if __name__ == "__main__":
    from manim_lamination_builder import Main
    from manim_lamination_builder.main import config

    config.preview = True
    # Main([double_orbit]).render()
    print(custom_dump(double_orbit))
    SigmaAnimation(double_orbit.convert_to_carrying()).render()
    

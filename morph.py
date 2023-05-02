from math import nan
from manim import WHITE, Scene, tempconfig, Mobject
from custom_json import custom_dump, custom_parse
from lamination import Lamination
from points import FloatWrapper, NaryFraction, UnitPoint
from typing import Tuple, Union
from animation import AnimateLamination


def remove_occluded(
    ret: Lamination, occlusion: Tuple[NaryFraction, NaryFraction]
) -> Lamination:
    def criteria(point):
        return (
            point.to_float() < occlusion[0].to_float()
            or point.to_float() > occlusion[1].to_float()
        )

    ret.points = list(filter(criteria, ret.points))
    ret.polygons = list(filter(lambda polly: criteria(polly[0]), ret.polygons))
    return ret


def morph_function(x: float, occlusion: Tuple[UnitPoint, UnitPoint]) -> float:
    a, b = occlusion[0].to_float(), occlusion[1].to_float()
    attracting_point = (a + b) / 2
    repelling_point = (attracting_point + 0.5) % 1
    bite_length = b - a
    remaining_length = 1 - bite_length

    relative_x = (x - repelling_point) % 1
    if x < a:
        relative_y = relative_x / remaining_length - 1
    elif x > repelling_point:
        relative_y = relative_x / remaining_length
    elif x > b:
        relative_y = 1 - ((1 - relative_x) / remaining_length) - 1
    else:
        relative_y = 0.5 - 1
    return (relative_y + repelling_point)


def result(lam: Lamination) -> Lamination:
    def mapping(p: UnitPoint) -> UnitPoint:
        assert lam.occlusion is not None
        return FloatWrapper(morph_function(p.to_float(), lam.occlusion))

    return lam.apply_function(mapping)


class MorphOcclusion(AnimateLamination):
    def __init__(
        self,
        initial: Lamination,
        occlusion: Tuple[NaryFraction, NaryFraction],
        start_mobject: Union[Mobject, None] = None,
        **kwargs,
    ) -> None:
        initial.occlusion = occlusion
        reported_initial = remove_occluded(initial, occlusion)
        reported_final = result(initial)
        super().__init__(reported_initial, reported_final, **kwargs)


class MyScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        initial = custom_parse(
            """{
        "polygons": [["0_003", "0_030", "0_300"],
          ["1_003", "3_030", "3_300"],
          ["2_003", "2_030", "2_300"],
          ["3_003", "1_030", "1_300"]],
        "chords": [],
        "points": [],
        "radix": 4}"""
        )
        assert isinstance(initial, Lamination)
        occlusion = (initial.polygons[0][0], initial.polygons[0][2])
        self.play(MorphOcclusion(initial, occlusion, run_time=5))


if __name__ == "__main__":
    from points import FloatWrapper
    import numpy as np
    import matplotlib.pyplot as plt
    from morph import morph_function

    x_values = np.linspace(0, 1, 1000)
    y_values = []
    # 
    # (FloatWrapper(0.2), FloatWrapper(0.8))
    morph_function(.62, (FloatWrapper(0.011904761904761904), FloatWrapper(0.19047619047619047)))
    for x in x_values:
        y = morph_function(x, (FloatWrapper(0.011904761904761904), FloatWrapper(0.19047619047619047)))
        y_values.append(y)
    plt.plot(x_values, y_values, 1, 1)
    plt.show()
    # with tempconfig({"quality": "medium_quality", "preview": True}):
    #     scene = MyScene()
    #     scene.render()


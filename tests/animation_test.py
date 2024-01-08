from manim import *
from manim_lamination_builder import custom_parse, GapLamination, AnimateLamination
from manim_lamination_builder.constructions import sigma
from manim_lamination_builder.points import CarryingFloatWrapper
from manim_lamination_builder.pull_backs import CriticalTree, rabbit_nth_pullback

config.preview = True
config.frame_height /= 3.7
config.frame_width /= 3.7


def test_centering():
    center = CarryingFloatWrapper(0)
    x = CarryingFloatWrapper(0.9, 2)
    res = x.centered(center)
    assert abs(res.to_float() - -0.1) < 0.000001
    assert sigma(res).to_float() < res.to_float()


def test_filter():
    thing = CriticalTree.default()
    rabbit_cord = thing.all_branches_identifyers()
    shared_starting_point = rabbit_nth_pullback(4).convert_to_carrying()
    init = shared_starting_point.filtered(rabbit_cord[0])
    assert len(init.polygons) == 4

    init = (
        shared_starting_point.filtered(rabbit_cord[1])
        .convert_to_carrying()
        .apply_function(lambda p: p.centered(CarryingFloatWrapper(0)))
    )

    assert len(init.polygons) == 4
test_filter()

class _MyScene(Scene):
    def construct(self):
        rabbit_cord = CriticalTree.default().all_branches_identifyers()
        shared_starting_point = rabbit_nth_pullback(7).convert_to_carrying()
        init = shared_starting_point.filtered(rabbit_cord[0])
        final = sigma(init)
        mob = init.build()
        self.add(mob)
        self.wait(1)
        self.play(AnimateLamination(init, final, mob))

        self.wait(1)
        self.clear()
        init = (
            shared_starting_point.filtered(rabbit_cord[1])
            .convert_to_carrying()
            .apply_function(lambda p: p.centered(CarryingFloatWrapper(0)))
        )
        final = sigma(init)
        mob = init.build()
        self.add(mob)
        self.wait(1)
        self.play(AnimateLamination(init, final, mob))

        self.wait(2)


if __name__ == "__main__":
    _MyScene().render()

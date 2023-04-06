from typing import List
from manim import (
    WHITE,
    Animation,
    Scene,
    tempconfig,
    Arc,
    Dot,
    RED,
    VMobject,
)
from chord import Chord, make_and_append_bezier
from lamination import Lamination
from points import NaryFraction, angle_to_cartesian


class OrientedChord:  # composition
    pass


# in Lamination
#    def apply_function


def lerp(a: float, b: float, alpha: float) -> float:
    "Linearly interpolate between two floats a and b using time value alpha."
    return (1 - alpha) * a + alpha * b


class AnimateLamination(Animation):
    def __init__(
        self,
        initial: Lamination,
        final: Lamination,
        # included_regions: List[OrientedChord],
        **kwargs,
    ) -> None:
        super().__init__(initial.build(), **kwargs)
        self.initial = initial
        self.final = final

    def interpolate_mobject(self, alpha: float) -> None:
        # lamination_radius = 1
        count_arcs = 0
        count_polygons = 0
        for i, submobject in enumerate(self.mobject.submobjects):
            if isinstance(submobject, Dot):
                # Set the position of the Dot based on its position in the list of submobjects
                print(alpha)
                index_in_list_of_points = i - count_polygons - count_arcs
                point_initial = self.initial.points[index_in_list_of_points]
                point_final = self.final.points[index_in_list_of_points]
                print(
                    angle_to_cartesian(
                        lerp(point_initial.to_angle(), point_final.to_angle(), alpha)
                    ))
                self.mobject.submobjects[i] = Dot(
                    angle_to_cartesian(
                        lerp(point_initial.to_angle(), point_final.to_angle(), alpha)
                    ),
                    color=RED,
                    radius=0.04,
                )
            elif isinstance(submobject, Arc):
                count_arcs += 1
                continue
            else:
                assert isinstance(submobject, VMobject)
                # Set the position of all the points for the submobject based on its position in the list of submobjects
                count_polygons += 1
                index_in_list_of_vmobjects = i - count_arcs
                if index_in_list_of_vmobjects < len(
                    self.initial.polygons
                ):  # TODO: polygons
                    polygon_initial = self.initial.polygons[index_in_list_of_vmobjects]
                    polygon_final = self.final.polygons[index_in_list_of_vmobjects]
                else:  # chord
                    chord_initial = self.initial.chords[
                        index_in_list_of_vmobjects - len(self.initial.polygons)
                    ]
                    chord_final = self.final.chords[
                        index_in_list_of_vmobjects - len(self.initial.polygons)
                    ]
                    a = lerp(
                        chord_initial.min.to_angle(),
                        chord_final.min.to_angle(),
                        alpha,
                    )
                    b = lerp(
                        chord_initial.max.to_angle(),
                        chord_final.max.to_angle(),
                        alpha,
                    )
                    submobject.reset_points()
                    make_and_append_bezier(submobject, a, b)


class MyScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # TODO: alter build() to no longer alter the Lamination by separaiting the populait action
        initial = Lamination(
            [],
            [
                Chord(
                    NaryFraction.from_string(4, "_03"),
                    NaryFraction.from_string(4, "_02"),
                )
            ],
            [NaryFraction.from_string(4, "_03"), NaryFraction.from_string(4, "_02")],
            4,
        )
        final = Lamination(
            [],
            [
                Chord(
                    NaryFraction.from_string(4, "_30"),
                    NaryFraction.from_string(4, "_20"),
                )
            ],
            [NaryFraction.from_string(4, "_30"), NaryFraction.from_string(4, "_20")],
            4,
        )
        self.play(AnimateLamination(initial, final, run_time=5))


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = MyScene()
        scene.render()

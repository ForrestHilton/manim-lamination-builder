from manim import WHITE, Animation, Scene, tempconfig, Arc, Dot, RED, VMobject
from chord import Chord, make_and_append_bezier
from custom_json import custom_parse
from lamination import Lamination
from points import NaryFraction, angle_to_cartesian


class OrientedChord:  # composition
    pass


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

    def interpolate(self, alpha: float) -> None:
        # lamination_radius = 1
        count_arcs = 0
        count_polygons = 0
        for i, submobject in enumerate(self.mobject.submobjects):
            if isinstance(submobject, Dot):
                # Set the position of the Dot based on its position in the list of submobjects
                index_in_list_of_points = i - count_polygons - count_arcs
                point_initial = self.initial.points[index_in_list_of_points]
                point_final = self.final.points[index_in_list_of_points]
                submobject.move_arc_center_to(
                    angle_to_cartesian(
                        lerp(point_initial.to_angle(), point_final.to_angle(), alpha)
                    )
                )
            elif isinstance(submobject, Arc):
                count_arcs += 1
                continue
            else:
                assert isinstance(submobject, VMobject)
                # Set the position of all the points for the submobject based on its position in the list of submobjects
                count_polygons += 1
                index_in_list_of_vmobjects = i - count_arcs
                if index_in_list_of_vmobjects < len(self.initial.polygons):
                    polygon_initial = self.initial.polygons[index_in_list_of_vmobjects]
                    polygon_final = self.final.polygons[index_in_list_of_vmobjects]

                    submobject.reset_points()
                    for i in range(3):
                        a = lerp(
                            polygon_initial[i].to_angle(),
                            polygon_final[i].to_angle(),
                            alpha,
                        )
                        b = lerp(
                            polygon_initial[(i + 1) % len(polygon_final)].to_angle(),
                            polygon_final[(i + 1) % len(polygon_final)].to_angle(),
                            alpha,
                        )
                        make_and_append_bezier(submobject, a, b)
                else:  # chord
                    chord_initial = self.initial.chords[
                        index_in_list_of_vmobjects - len(self.initial.polygons)
                    ]
                    chord_final = self.final.chords[
                        index_in_list_of_vmobjects - len(self.initial.polygons)
                    ]
                    a = lerp(
                        chord_initial.min.to_angle(), chord_final.min.to_angle(), alpha
                    )
                    b = lerp(
                        chord_initial.max.to_angle(), chord_final.max.to_angle(), alpha
                    )
                    submobject.reset_points()
                    make_and_append_bezier(submobject, a, b)


class MyScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # TODO: alter build() to no longer alter the Lamination by separaiting the populait action
        initial = custom_parse(
            """
 {
    "polygons": [["1.0_003", "3.0_030", "3.0_300"]],
    "points":["0_003", "0_030", "0_300"],
    "radix": 4
  }
                     """
        )

        final = custom_parse(
            """
 {
    "polygons": [["1_003", "3_030", "3_300"]],
    "points":["1_003", "3_030", "3_300"],
    "radix": 4
  }
                     """
        )
        self.play(AnimateLamination(final, initial, run_time=5))


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = MyScene()
        scene.render()

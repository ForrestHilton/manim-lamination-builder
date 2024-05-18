"""
This is a re-implementation of lamination-builder that runs in python without dependencies on a browser and focusing on animations and convenient generation of figures. Instead it uses Manim, which has several dependencies, which you are responsible for installing in accordance with Manim's installation instructions.
"""

from manim_lamination_builder.lamination import (
    GapLamination,
    LeafLamination,
    AgnosticLamination,
    Polygon,
)
from manim_lamination_builder.custom_json import (
    custom_dump,
    custom_parse,
    read_file_to_laminations,
    parse_lamination,
)
from manim_lamination_builder.points import FloatWrapper, NaryFraction, Angle
from manim_lamination_builder.animation import AnimateLamination, SigmaAnimation
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.new_generate import next_pull_back
from manim_lamination_builder.pull_back_tree import TreeRender, PullBackTree
from manim_lamination_builder.main import group, Main
from manim_lamination_builder.morph import (
    HalfOpenArc,
    OccludedLamination,
    interpolate_quotent_of_region_of_rotational_polygon,
)
import manim_lamination_builder.__main__
from manim_lamination_builder.visual_settings import VisualSettings, get_color
from manim_lamination_builder.sibling_trees import (
    first_polygon,
    make_regions,
    construct_nested_tuple,
    construct_tree,
)
from manim_lamination_builder.constructions import (
    double_orbit,
    uniquely_color,
    unicritical_polygon,
    add_points_preimages,
    fussCatalan,
    sigma,
    pollygons_are_one_to_one
)
from manim_lamination_builder.pull_backs import CriticalTree, rabbit_nth_pullback, FDL

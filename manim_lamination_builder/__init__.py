"""
This is a re-implementation of lamination-builder that runs in python without dependencies on a browser and focusing on animations and convenient generation of figures. Instead it uses Manim, which has several dependencies, which you are responsible for installing in accordance with Manim's installation instructions.
"""

import manim_lamination_builder.__main__
from manim_lamination_builder.animation import AnimateLamination, SigmaAnimation
from manim_lamination_builder.chord import Chord
from manim_lamination_builder.constructions import (
    add_points_preimages,
    double_orbit,
    fussCatalan,
    pollygons_are_one_to_one,
    unicritical_polygon,
    uniquely_color,
)
from manim_lamination_builder.custom_json import (
    custom_dump,
    custom_parse,
    parse_lamination,
    read_file_to_laminations,
    str_to_laminations,
)
from manim_lamination_builder.lamination import (
    AgnosticLamination,
    GapLamination,
    LeafLamination,
    Polygon,
)
from manim_lamination_builder.main import Main, group
from manim_lamination_builder.malaugh import phi, psi
from manim_lamination_builder.morph import (
    HalfOpenArc,
    OccludedLamination,
    interpolate_quotent_of_region_of_rotational_polygon,
)
from manim_lamination_builder.new_generate import next_pull_back
from manim_lamination_builder.orbits import Orbit 
from manim_lamination_builder.points import Angle, FloatWrapper, NaryFraction, sigma
from manim_lamination_builder.pull_back_tree import PullBackTree, TreeRender
from manim_lamination_builder.pull_backs import FDL, CriticalTree, rabbit_nth_pullback
from manim_lamination_builder.sibling_trees import (
    construct_nested_tuple,
    construct_tree,
    first_polygon,
    make_regions,
)
from manim_lamination_builder.visual_settings import VisualSettings, get_color

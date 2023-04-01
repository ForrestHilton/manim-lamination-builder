#!/usr/bin/env python3
# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from custom_json import CustomDecoder
from typing import List
from manim import (
    WHITE,
    Scene,
    Group,
    tempconfig,
)
import sys
import os
import json

from manim.utils.file_ops import config

from points import NaryFraction
from chord import Chord
from lamination import Lamination, Chord


class Main(Scene):
    def __init__(self, laminations: List[Lamination]):
        self.laminations = laminations
        super().__init__()

    def construct(self):
        self.camera.background_color = WHITE
        group = Group(*[lamination.build() for lamination in self.laminations])
        group = group.arrange_in_grid()
        group.scale(
            1
            / max(group.width / config.frame_width, group.height / config.frame_height)
        )
        self.add(group)


if __name__ == "__main__":
    file = sys.argv[-1]
    if len(sys.argv) == 1:
        path = "/home/forrest/Desktop/manim_lamination_builder/test.json"
    else:
        path = os.path.join(os.getcwd(), file)
    with open(path) as f:
        data = json.load(f, cls=CustomDecoder)
    laminations = data

    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = Main(laminations)
        scene.render()

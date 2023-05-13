#!/usr/bin/env python3
# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from manim_lamination_builder.custom_json import custom_dump, read_file_to_laminations
from typing import List
from manim import (
    WHITE,
    Scene,
    Group,
    tempconfig,
)
import sys
import os

from manim.utils.file_ops import config

from manim_lamination_builder.lamination import Lamination

def group(laminations: List[Lamination]):
    group = Group(*[lamination.build() for lamination in laminations])
    group = group.arrange_in_grid()
    group.scale(
        1
        / max(group.width / config.frame_width + 0.01, group.height / config.frame_height + 0.01)
    )
    return group

class Main(Scene):
    def __init__(self, laminations: List[Lamination]):
        self.laminations = laminations
        super().__init__()

    def construct(self):
        self.camera.background_color = WHITE
        self.add(group(self.laminations))


if __name__ == "__main__":
    file = sys.argv[-1]
    if len(sys.argv) == 1:
        path = "/home/forrest/Desktop/manim_lamination_builder/test.json5"
    else:
        path = os.path.join(os.getcwd(), file)
    laminations = read_file_to_laminations(path)
    for lamination in laminations:
        lamination.auto_populate()

    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = Main(laminations)
        scene.render()

# WORK IN PROGRESS
This is a re-implementation of [lamination-builder](https://csfalcione.github.io/lamination-builder/) that runs in python without dependencies on a browser and focusing on animations and convenient generation of figures. Instead it uses [Manim](https://github.com/ManimCommunity/manim/), and which has several dependencies. 


# Installation:
Please refer to [to manim's installation instructions](https://docs.manim.community/en/stable/installation.html). It and its dependencies are required, with the possible exception of tex. Afterward, you can simply run
```
pip install manim_lamination_builder
```

# Usage: 
## render multiple laminations in one image
```
python -m manim_lamination_builder file.json
```
The input format is as follows: A list of laminations to be placed in the figure (tilling is a best effort left to right and top to bottom Placemen). The blank lamination is permitted.
```
[
  {
    polygons:[["_001","_010","_100"]],
    chords:[["_1","2"]],
    points: ["3"],
    radix: 4
  },
  {
    "polygons": [["0_003", "0_030", "0_300"], 
      ["1_003", "3_030", "3_300"], 
      ["2_003", "2_030", "2_300"], 
      ["3_003", "1_030", "1_300"]], 
    "chords": [], 
    "points": [], 
    "radix": 4
  },
  { radix: 4}
]
```
![please enable images](https://github.com/ForrestHilton/python-lamination-builder/blob/main/contrived_example.png "Render of json above")

## generate and render laminations to verify my research
```
from manim import tempconfig
from manim_lamination_builder import generate_unicritical_lamination, Main


with tempconfig({"quality": "high_quality", "preview": True}):
    Main(generate_unicritical_lamination(4, 3)).render()
```
![please enable images](https://github.com/ForrestHilton/python-lamination-builder/blob/main/example.png "Example Output from my Reasearch")

## animate the leaves and points moving to their images
Please not that sigma_d is understood as a dilation of angular position with wrapping, so the forgotten digit is recorded and used to determine how many times to wrap around. 
```
from manim import Scene, WHITE, tempconfig
from manim_lamination_builder import (
    parse_lamination,
    curried_colorize_with_respect_to,
    sigma,
    AnimateLamination,
)


class MyScene(Scene):
    def construct(self):
        initial = parse_lamination(
            '{polygons: [["_200","_002","_020"]], points:[0.1,"200","201"], radix: 3 }'
        )

        initial.auto_populate()
        initial.colorizer = curried_colorize_with_respect_to(initial.polygons[0])
        final = initial.apply_function(sigma)
        mob = initial.build(3)
        mob.submobjects[2].set_color("#008080")
        self.add(mob)
        self.wait(2)
        self.play(AnimateLamination(initial, final, start_mobject=mob, run_time=5))
        self.wait(2)


with tempconfig(
    {"quality": "high_quality", "preview": True, "background_color": WHITE}
):
    scene = MyScene()
    scene.render()
```

# Developments

Feature requests will be entertained, however this is intended to be used in combination with other tools like latex and your own python scripts. I hope this is a reasonable API.

# License
Licensed under the The AGPLv3 License (AGPLv3)
Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

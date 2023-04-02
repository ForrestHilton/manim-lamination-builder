# WORK IN PROGRESS -- THE FEATURES NOT USED IN THE EXAMPLE DON'T WORK YET

This is a re-implementation of [lamination-builder](https://csfalcione.github.io/lamination-builder/) that runs in python without dependencies on a browser and focusing on convenient generation of figures. Instead it uses [Manim](https://github.com/ManimCommunity/manim/), and which has several dependencies. 

The input format is as follows: A list of laminations to be placed in the figure (tilling is a best effort left to right and top to bottom Placemen based on a 16:9 screen). The blank lamination is permited.

Each lamination may have of the following fields: polygons, chords (must be a list of lists of length two), point_lables, point_colors ("*" for default color which defaults to red), and points. Omissions in each field will be filled based on the fields that proceed it in the list above. Each lamination must have a "radix" which is the base.

# Example:
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

# Installation: (correct python packaging is on the TODO list)
Please refer to [to manim's installation instructions](https://docs.manim.community/en/stable/installation.html). It and its dependencies are required, with the possible exception of tex.
```
pip install manim json json5
git clone https://github.com/ForrestHilton/python-lamination-builder
```

Add the project to you PYTHONPATH in a settings file, if you wish to import the python files.

# Usage: 
```
/path/to/python-lamination-builder/main.py file.json
```


Feature requests will be entertained. I have yet to see a need for any of the following features: mapping forward, pull backs, automatically placing descriptions or tittles at the top. This is intended to be used in combination with other tools like latex and your own python scripts. I hope this is a reasonable API.


# example output from my research
![please enable images](https://github.com/ForrestHilton/python-lamination-builder/blob/main/example.png "Example Output from my Reasearch")

# License
Licensed under the The AGPLv3 License (AGPLv3)
Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

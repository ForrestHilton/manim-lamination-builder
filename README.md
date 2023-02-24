This is a re-implementation of [lamination-builder](https://csfalcione.github.io/lamination-builder/) that runs in python without dependencies on a browser and focusing on convenient generation of figures. Instead it uses [Manim](https://github.com/ManimCommunity/manim/), and which has several dependencies. 

The input format is as follows: A list of laminations to be placed in the figure (tilling is a best effort left to righ and top to bottom Placemen based on a 16:9 screen). The blank lamination is permited.

Each lamination may have of the following fields: polygons, chords (must be a list of lists of length two), point_lables, point_colors ("*" for default color which defaults to red), and points. Omissions in each field will be filled based on the fields that proceed it in the list above. Each lamination must have a "radix" which is the base.

# Example:
```
[
  {
    "polygons":[["_001","_010","_100"]],
    "chords":[["_100","2"]],
    "point_lables": {"_001": "starting point", "_010": "maps to _100"},
    "point_colors": {"*": "blue", "_001": "red"},
    "points": ["1","2","_3"],
    "radix": 4
  },
  {
    "radix": 3
  }
]
```
# Usage: 
commandline TODO

Installation:
Follow the manim installation steps.

Feature requests will be entertained. I have yet to see a need for any of the following features: mapping forward, pull backs, automatically placing descriptions or tittles at the top. This is intended to be used in combination with other tools like latex and your own python scripts. I hope this is a reasonable API.



# License
Licensed under the The AGPLv3 License (AGPLv3)
Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

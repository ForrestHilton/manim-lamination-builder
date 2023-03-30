# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List
from chord import Chord
from lamination import Lamination
from points import NaryFraction
import json


class CustomEncoder(json.JSONEncoder):
    def default(self, v):
        types = {"NaryFraction": lambda v: v.to_string()}
        vtype = type(v).__name__
        if vtype == "Lamination":
            return v.__dict__
        if vtype == "Chord":
            return list(v.__dict__.values())
        if vtype in types:
            return types[type(v).__name__](v)
        else:
            return json.JSONEncoder.default(self, v)


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "radix" in dct:
            radix = dct["radix"]

            def string_handler(s):
                return NaryFraction.from_string(radix, s)

            def list_handler(list):
                assert isinstance(list, List)
                return [*map(string_handler, list)]

            polygons = [*map(list_handler, dct.get("polygons", []))]
            chords = [*map(lambda list: Chord(list[0], list[1]), dct.get("chords", []))]
            points = list_handler(dct.get("points", []))
            return Lamination(polygons, chords, points, radix)
        return dct

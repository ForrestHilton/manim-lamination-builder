# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from lamination import Lamination
from points import NaryFraction
import json


class CustomEncoder(json.JSONEncoder):
    def default(self, v):
        types = {"NaryFraction": lambda v: v.to_string()}
        vtype = type(v).__name__
        if vtype == "Lamination":
            return v.__dict__
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
                return [*map(string_handler, list)]

            if "polygons" in dct:
                polygons = [*map(list_handler, dct["polygons"])]
            else:
                polygons = None
            if "chords" in dct:
                chords = [*map(list_handler, dct["chords"])]
            else:
                chords = None
            if "points" in dct:
                points = list_handler(dct["points"])
            else:
                points = None
            return Lamination(polygons, chords, points, radix)
        return dct

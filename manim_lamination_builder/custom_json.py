# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List, Union
from manim_lamination_builder.lamination import Lamination
from manim_lamination_builder.points import FloatWrapper, NaryFraction
import json
import json5


class CustomEncoder(json.JSONEncoder):
    def default(self, v):
        types = {"NaryFraction": lambda v: v.to_string()}
        vtype = type(v).__name__
        if vtype in ["LeafLamination", "Lamination"]:
            ret = v.__dict__.copy()
            return ret
        if vtype == "Chord":
            return list(v.__dict__.values())
        if vtype == "FloatWrapper":
            return v.value
        if vtype in types:
            return types[type(v).__name__](v)
        if vtype == "set":
            return list(v)
        else:
            return json.JSONEncoder.default(self, v)


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "radix" in dct:
            radix = dct["radix"]

            def point_handler(v):
                if isinstance(v, float):
                    return FloatWrapper(v, radix)
                else:
                    return NaryFraction.from_string(radix, v)

            def list_handler(list):
                assert isinstance(list, List)
                return [*map(point_handler, list)]

            polygons = [*map(list_handler, dct.get("polygons", []))]
            points = list_handler(dct.get("points", []))
            occlusion = list_handler(dct.get("occlusion", []))
            if len(occlusion) == 0:
                occlusion = None
            else:
                assert len(occlusion) == 2
                occlusion = (occlusion[0], occlusion[1])
            return Lamination(polygons, points, radix, occlusion=occlusion)
        return dct


def preprocess_for_json5(json5_str: str) -> str:
    obj = json5.loads(json5_str)
    json_str = json.dumps(obj)
    return json_str


def read_file_to_laminations(path) -> List[Lamination]:
    with open(path) as f:
        json_str = preprocess_for_json5(f.read())
        return json.loads(json_str, cls=CustomDecoder)


def custom_dump(data_of_a_type_defined_in_this_project) -> str:
    return json.dumps(data_of_a_type_defined_in_this_project, cls=CustomEncoder)


def custom_parse(string: str) -> Union[Lamination, List[Lamination]]:
    json_str = preprocess_for_json5(string)
    return json.loads(json_str, cls=CustomDecoder)


def parse_lamination(string: str) -> Lamination:
    lam = custom_parse(string)
    assert isinstance(lam, Lamination)
    return lam

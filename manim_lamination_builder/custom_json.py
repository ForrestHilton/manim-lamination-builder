# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
from typing import List, Union

import json5

from manim_lamination_builder.chord import Chord
from manim_lamination_builder.lamination import (AbstractLamination,
                                                 GapLamination, LeafLamination)
from manim_lamination_builder.points import FloatWrapper, NaryFraction
from manim_lamination_builder.pull_back_tree import PullBackTree

# TODO: make custom_dump obsolete with good __repr__


class CustomEncoder(json.JSONEncoder):
    def default(self, v):
        types = {"NaryFraction": lambda v: v.to_string()}
        vtype = type(v).__name__
        if vtype in ["LeafLamination", "GapLamination", "PullBackTree"]:
            ret = v.__dict__.copy()
            return ret
        if vtype == "Chord":
            return list(v.__dict__.values())
        if vtype in ["FloatWrapper", "CarryingFloatWrapper"]:
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

    @staticmethod
    def inner_parse_lamination(dct):
        degree = dct["degree"]

        def point_handler(v):
            if isinstance(v, float):
                return FloatWrapper(v, degree)
            else:
                return NaryFraction.from_string(degree, v)

        def list_handler(ls):
            assert isinstance(ls, List)
            return [*map(point_handler, ls)]

        polygons = [*map(list_handler, dct.get("polygons", []))]
        leafs = [*map(list_handler, dct.get("leafs", []))]
        points = list_handler(dct.get("points", []))
        occlusion = list_handler(dct.get("occlusion", []))
        if len(occlusion) == 0:
            occlusion = None
        else:
            assert len(occlusion) == 2
            occlusion = (occlusion[0], occlusion[1])

        if dct.get("leafs", None) is not None:
            leafs = list(map(lambda l: Chord(l[0], l[1]), leafs))
            return LeafLamination(leafs=leafs, points=points, degree=degree)
        return GapLamination(polygons=polygons, points=points, degree=degree)

    @staticmethod
    def parse_tree(dct):
        node = dct.get("node")
        children = dct.get("children")

        return PullBackTree(node=node, children=children)

    def object_hook(self, dct):
        if "node" in dct:
            return CustomDecoder.parse_tree(dct)

        if "degree" in dct:
            return CustomDecoder.inner_parse_lamination(dct)
        return dct


def preprocess_for_json5(json5_str: str) -> str:
    obj = json5.loads(json5_str)
    json_str = json.dumps(obj)
    return json_str


def str_to_laminations(string) -> List["GapLamination"]:
    json_str = preprocess_for_json5(string)
    return json.loads(json_str, cls=CustomDecoder)


def read_file_to_laminations(path) -> List["GapLamination"]:
    with open(path) as f:
        json_str = preprocess_for_json5(f.read())
        return json.loads(json_str, cls=CustomDecoder)


def custom_dump(data_of_a_type_defined_in_this_project) -> str:
    return json.dumps(data_of_a_type_defined_in_this_project, cls=CustomEncoder)


def custom_parse(string: str) -> Union["GapLamination", List["GapLamination"]]:
    json_str = preprocess_for_json5(string)
    return json.loads(json_str, cls=CustomDecoder)


def parse_lamination(string: str) -> AbstractLamination:
    lam = custom_parse(string)
    assert isinstance(lam, AbstractLamination)
    return lam

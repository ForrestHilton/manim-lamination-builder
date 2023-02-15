from typing import List, Optional, Any, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Lamination:
    polygons: Optional[List[List[str]]]
    chords: Optional[List[List[str]]]
    points: Optional[List[str]]
    radix: int

    def __init__(
        self,
        polygons: Optional[List[List[str]]],
        chords: Optional[List[List[str]]],
        points: Optional[List[str]],
        radix: int,
    ) -> None:
        self.polygons = polygons
        self.chords = chords
        self.points = points
        self.radix = radix

    @staticmethod
    def from_dict(obj: Any) -> "Lamination":
        assert isinstance(obj, dict)
        polygons = from_union(
            [lambda x: from_list(lambda x: from_list(from_str, x), x), from_none],
            obj.get("polygons"),
        )
        chords = from_union(
            [lambda x: from_list(lambda x: from_list(from_str, x), x), from_none],
            obj.get("chords"),
        )
        points = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("points")
        )
        radix = from_int(obj.get("radix"))
        return Lamination(polygons, chords, points, radix)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.polygons is not None:
            result["polygons"] = from_union(
                [lambda x: from_list(lambda x: from_list(from_str, x), x), from_none],
                self.polygons,
            )
        if self.chords is not None:
            result["chords"] = from_union(
                [lambda x: from_list(lambda x: from_list(from_str, x), x), from_none],
                self.chords,
            )
        if self.points is not None:
            result["points"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.points
            )
        result["radix"] = from_int(self.radix)
        return result


def laminations_from_dict(s: Any) -> List[Lamination]:
    return from_list(Lamination.from_dict, s)


def laminations_to_dict(x: List[Lamination]) -> Any:
    return from_list(lambda x: to_class(Lamination, x), x)



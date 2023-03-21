# Licensed under the The AGPLv3 License (AGPLv3)
# Copyright (c) 2023 Forrest M. Hilton <forrestmhilton@gmail.com>
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import List, Optional

from points import NaryFraction


class Lamination:
    polygons: Optional[List[List[NaryFraction]]]
    chords: Optional[List[List[NaryFraction]]]
    points: Optional[List[NaryFraction]]
    radix: int

    def __init__(
        self,
        polygons: Optional[List[List[NaryFraction]]],
        chords: Optional[List[List[NaryFraction]]],
        points: Optional[List[NaryFraction]],
        radix: int,
    ) -> None:
        self.polygons = polygons
        self.chords = chords
        self.points = points
        self.radix = radix

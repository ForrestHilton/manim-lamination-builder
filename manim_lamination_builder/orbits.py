import numpy as np

from manim_lamination_builder.points import NaryFraction


class PeriodicOrbit:
    def __init__(
        self,
        point: NaryFraction
        ):
        self.temporal_orbit, self.spacial_orbit = self._full_orbits(point)

    def __str__(self):
        return "[" + ", ".join(str(to) for to in self.temporal_orbit) + "]"

    def __eq__(self, other):
        if not isinstance(other, PeriodicOrbit):
            return NotImplemented
        if len(self.temporal_orbit) != len(other.temporal_orbit):
            return False
        if self.temporal_orbit[0] in other.temporal_orbit:
            return True
        return False

    @classmethod
    def from_point(cls, point:NaryFraction):
        "Superfluous"
        return PeriodicOrbit(point)

    @classmethod
    def from_dep_seq_and_rot_num(cls, deployment_sequence: list, rotation_number: list):
        return PeriodicOrbit(cls._goldberg_orbit(deployment_sequence, rotation_number))

    @classmethod
    def from_dep_seq_and_jump_over_seq(cls, deployment_sequence: list, jump_over_sequence: list):
        return PeriodicOrbit(cls._jump_over_orbit(deployment_sequence, jump_over_sequence))

    def get_jump_over_sequence(self):
        jos = []
        length = len(self.temporal_orbit)
        for ti, tp in enumerate(self.temporal_orbit):
            if ti == 0:
                prev_index = 0
                continue
            for si, sp in enumerate(self.spacial_orbit):
                if sp == tp:
                    if si > prev_index:
                        jos += [si - prev_index]
                    else:
                        jos += [length - prev_index + si]
                    prev_index = si
        s = sum(jos)
        jos += [length - (s % length)]
        return jos

    # returns a full orbit in spacial order
    def _full_orbits(self, point: NaryFraction):
        assert (
            len(point.exact) == 0 and len(point.repeating) != 0
        ), "must be periodic point"
        p = point
        fOrbit = []
        sOrbit = []
        tOrbit = []
        for i in range(len(point.repeating)):
            p = p.after_sigma()
            fOrbit += [p]
        sOrbit = sorted(fOrbit)
        startPoint = sOrbit[0]
        startIndex = fOrbit.index(startPoint)
        l = len(fOrbit)
        for i in range(l):
            tOrbit += [fOrbit[(startIndex + i) % l]]
        temporal_orbit = tuple(tOrbit)
        spacial_orbit = tuple(sOrbit)
        return temporal_orbit, spacial_orbit

    @classmethod
    def _goldberg_orbit(cls, deployment_sequence, rotation_number):
        fps = cls._make_fixed_point_sequence(deployment_sequence)
        fpe = cls._make_fixed_point_expansion(fps)
        od = cls._make_orbit_digits(fpe, rotation_number)
        de = cls._make_radix_expansion(od, rotation_number)
        return NaryFraction([], de, len(deployment_sequence) + 1)

    @classmethod
    def _jump_over_orbit(cls, deployment_sequence, jump_over_sequence):
        fps = cls._make_fixed_point_sequence(deployment_sequence)
        fpe = cls._make_fixed_point_expansion(fps)

        # get temporal fpe
        orbit_length = len(jump_over_sequence)
        tfpe = [fpe[0]]
        i = 0
        for j in range(len(fpe) - 1):
            i = (i + jump_over_sequence[j]) % orbit_length
            tfpe += [fpe[i]]

        # get temporal AR sequence
        tar = []
        i = 0
        for j in range(len(fpe)):
            i = i + jump_over_sequence[j]
            if i >= orbit_length:
                tar += ["-"]
                i %= orbit_length
            else:
                tar += ["+"]

        # get final orbit
        for i, ar in enumerate(tar):
            if ar == "-":
                tfpe[i] += 1
        orbit = NaryFraction(
            exact=(), repeating=tfpe, degree=len(deployment_sequence) + 1
        )

        return orbit

    # input list deployment sequence: depSeq
    def _make_fixed_point_sequence(dep_seq):
        fixed_point_sequence = []
        i = 0
        for n in dep_seq:
            if i == 0:
                fixed_point_sequence.append(n)
            else:
                fixed_point_sequence.append(n - dep_seq[i - 1])
            i = i + 1
        return fixed_point_sequence

    # input list fixed point sequence: fps
    def _make_fixed_point_expansion(fps):
        fixedPointExpansion = []
        j = 0
        for n in fps:
            for i in range(n):
                fixedPointExpansion.append(j)
            j = j + 1
        return fixedPointExpansion

    # input list fixed point expansion: fpe, list rotation number: rn
    def _make_orbit_digits(fpe, rn):
        orbitDigits = []
        adv = rn[1] - rn[0]
        for i in range(len(fpe)):
            if i < adv:
                orbitDigits.append(fpe[i])
            else:
                orbitDigits.append(fpe[i] + 1)
        return orbitDigits

    # input list orbit digits: od, list rotation number: rn
    def _make_radix_expansion(od, rn):
        assert (
            rn[0] != 0 and rn[1] != 0
        ), "Rotation number should not have 0 as either number."
        factor = np.gcd(rn[0], rn[1])
        step = rn[0]
        base = rn[1]
        dNaryExpansion = []
        dneTemp = []
        for k in range(factor):
            for n in range(int(base / factor)):
                dneTemp.append(od[((n * step) + k) % base])
            dNaryExpansion.append(dneTemp)
            dneTemp = []
        return dNaryExpansion[0]


class AllOrbits:
    iter_index = 0

    def __init__(self, degree: int, length: int):
        self.degree = degree
        self.length = length
        self.orbits = self._init_orbits()

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        self.iter_index += 1
        if self.iter_index > len(self.orbits):
            raise StopIteration
        return self.orbits[self.iter_index - 1]

    def _init_orbits(self):
        total = self.degree**self.length
        point = [0]
        orbitList = [
            PeriodicOrbit(NaryFraction(exact=(), repeating=point, degree=self.degree))
        ]
        for i in range(total - 1):
            point = self._increment_baseN(point, self.degree)
            point = self._pad_with_zeros(point, self.length)
            if self._is_new_orbit(point, orbitList):
                orbitList.append(
                    PeriodicOrbit(
                        NaryFraction(exact=(), repeating=point, degree=self.degree)
                    )
                )
        return orbitList

    def _increment_baseN(self, input_num, base):
        num = input_num[:]
        num.reverse()
        outputNum = []
        tempNum = 0
        carry = 1

        for i in range(len(num)):
            tempNum = num[i] + carry
            if tempNum >= base:
                tempNum %= base
                carry = 1
            else:
                carry = 0
            outputNum.append(tempNum)

        if carry == 1:
            outputNum.append(carry)

        outputNum.reverse()
        return outputNum

    def _pad_with_zeros(self, input_list, total_length):
        input_list.reverse()
        numZeros = total_length - len(input_list)
        numZeros = numZeros if numZeros >= 0 else 0
        for i in range(numZeros):
            input_list.append(0)
        input_list.reverse()
        return input_list

    def _is_new_orbit(self, new_point: list, orbits: list):
        orbitLength = len(new_point)
        rotPoint = new_point
        newOrbit = PeriodicOrbit(
            NaryFraction(exact=(), repeating=rotPoint, degree=self.degree)
        )
        for i in range(len(orbits)):
            # print(str(orbits[i]) + "; " + str(newOrbit))
            # print()
            if orbits[i] == newOrbit:
                return False
        return True

    def _rotate_point(self, point):
        newPoint = point[1:] + point[:1]
        return newPoint


def main():
    ds = [5, 5]
    jos = [2,2,2,2,2]
    rn = [2,5]
    jo = PeriodicOrbit.from_dep_seq_and_jump_over_seq(ds,jos)
    print(jo)
    print(jo.get_jump_over_sequence())
    ro = PeriodicOrbit.from_dep_seq_and_rot_num(ds,rn)
    print(ro)
    po = PeriodicOrbit.from_point(NaryFraction(exact=(),repeating=(1,0,1,0,0),degree=3))
    print(po)

    return


if __name__ == "__main__":
    # sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()

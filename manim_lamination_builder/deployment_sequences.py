import numpy as np


# TODO: review for code duplication
def increment_baseN(inputNum, base):
    num = inputNum[:]
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


def pad_with_zeros(input_list, total_length):
    input_list.reverse()
    numZeros = total_length - len(input_list)
    numZeros = numZeros if numZeros >= 0 else 0
    for i in range(numZeros):
        input_list.append(0)
    input_list.reverse()
    return input_list


def list_orbits(base, length):
    total = base**length
    point = [0]
    orbitList = [pad_with_zeros(point, length)]
    for i in range(total - 1):
        point = increment_baseN(point, base)
        point = pad_with_zeros(point, length)
        if is_new_orbit(point, orbitList):
            orbitList.append(point)

    return orbitList


def is_new_orbit(newPoint, orbits):
    orbitLength = len(orbits[0])
    newOrbit = []
    rotPoint = newPoint
    for i in range(orbitLength):
        rotPoint = rotate_point(rotPoint)
        newOrbit.append(rotPoint)
    for i in range(len(orbits)):
        if orbits[i] in newOrbit:
            return False
    return True


def rotate_point(point):
    newPoint = point[1:] + point[:1]
    return newPoint


def flatten_point(point: list):
    fp = 0
    l = len(point)
    for j in range(l):
        fp += point[l - j - 1] * (10**j)
    return fp


def expand_point(point: int):
    ep = [int(digit) for digit in str(point)]
    return ep


def get_fixed_points(base, length):
    fixedPoints = []
    for i in range(base - 1):
        fp = []
        for j in range(length):
            fp.append(i + 1)
        fixedPoints.append(flatten_point(fp))
    return fixedPoints


def deployment_sequence(input_point, base):
    depSeq = [0] * (base - 1)
    point = input_point[:]
    fixedPoints = get_fixed_points(base, len(point))

    for i in range(len(point)):
        pointNum = flatten_point(point)

        for f in fixedPoints:
            if pointNum == f or pointNum == 0:
                return "fp"

        for f in range(len(fixedPoints)):
            if pointNum < fixedPoints[f]:
                depSeq[f] += 1
        point = rotate_point(point)

    return depSeq


# TODO: maybe provide a doc string
def count_deployment_sequences(deployment_sequences):
    depSeqCount = []

    for ds in deployment_sequences:
        new = 1
        if ds != "fp":
            for sc in depSeqCount:
                if ds == sc[0]:
                    sc[1] += 1
                    new = 0
            if new:
                depSeqCount.append([ds, 1])

    return depSeqCount


def list_deployment_sequences(orbits, base):
    depSeqs = []
    for i in range(len(orbits)):
        depSeqs.append(deployment_sequence(orbits[i], base))
    return depSeqs


# returns a full orbit in spacial order
def full_orbits(point):
    p = point[:]
    fOrbit = []
    sOrbit = []
    tOrbit = []
    for i in range(len(point)):
        p = rotate_point(p)
        fOrbit += [p]
    flOrbit = [flatten_point(fo) for fo in fOrbit]
    flOrbit = quicksort(flOrbit)
    for fl in flOrbit:
        for f in fOrbit:
            if fl == flatten_point(f):
                sOrbit += [f]
    startPoint = flOrbit[0]
    startIndex = flOrbit.index(startPoint)
    l = len(flOrbit)
    for i in range(l):
        tOrbit += [fOrbit[(startPoint + i) % l]]
    return (tOrbit, sOrbit)


def quicksort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        less = [i for i in arr[1:] if i <= pivot]
        greater = [i for i in arr[1:] if i > pivot]
        return quicksort(less) + [pivot] + quicksort(greater)


def is_rotational(Point: list) -> bool:
    fullOrbit = full_orbits(Point)
    tOrbit = fullOrbit[:1]
    sOrbit = fullOrbit[1:]
    l = len(Point)
    prevDiff = 0
    prevIndex = 0
    for to in tOrbit:
        for index, so in enumerate(sOrbit):
            if index == 0:
                break
            if so == to:
                if prevIndex == 0:
                    prevDiff = index
                    prevIndex = index
                    break
                else:
                    if index < prevIndex:
                        currentDiff = (l + index) - prevIndex
                    else:
                        currentDiff = index - prevIndex
                    if currentDiff != prevDiff:
                        return False
                    else:
                        prevIndex = index
                        break
    return True


# TODO:remove
def main():
    D = 3
    Q = 3
    # new = isNewOrbit([2,1,0,0],[[0,2,1,0]])
    # print(new)
    # orbits = listOrbits(D,Q)
    # print(orbits)
    # print(len(orbits))
    o = [0, 0, 0, 0, 1]
    print(full_orbits(o))
    print(is_rotational(o))
    return


if __name__ == "__main__":
    # sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()

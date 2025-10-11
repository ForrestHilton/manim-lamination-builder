import numpy as np


def incrementBaseN(inputNum, base):
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


def padWithZeros(inputList, totalLength):
    inputList.reverse()
    numZeros = totalLength - len(inputList)
    numZeros = numZeros if numZeros >= 0 else 0
    for i in range(numZeros):
        inputList.append(0)
    inputList.reverse()
    return inputList


def listOrbits(base, length):
    total = base**length
    point = [0]
    orbitList = [padWithZeros(point, length)]
    for i in range(total - 1):
        point = incrementBaseN(point, base)
        point = padWithZeros(point, length)
        if isNewOrbit(point, orbitList):
            orbitList.append(point)

    return orbitList


def isNewOrbit(newPoint, orbits):
    orbitLength = len(orbits[0])
    newOrbit = []
    rotPoint = newPoint
    for i in range(orbitLength):
        rotPoint = rotatePoint(rotPoint)
        newOrbit.append(rotPoint)
    for i in range(len(orbits)):
        if orbits[i] in newOrbit:
            return False
    return True


def rotatePoint(point):
    newPoint = point[1:] + point[:1]
    return newPoint


def flattenPoint(point: list):
    fp = 0
    l = len(point)
    for j in range(l):
        fp += point[l - j - 1] * (10**j)
    return fp


def expandPoint(point: int):
    ep = [int(digit) for digit in str(point)]
    return ep


def getFixedPoints(base, length):
    fixedPoints = []
    for i in range(base - 1):
        fp = []
        for j in range(length):
            fp.append(i + 1)
        fixedPoints.append(flattenPoint(fp))
    return fixedPoints


def deploymentSequence(inputPoint, base):
    depSeq = [0] * (base - 1)
    point = inputPoint[:]
    fixedPoints = getFixedPoints(base, len(point))

    for i in range(len(point)):
        pointNum = flattenPoint(point)

        for f in fixedPoints:
            if pointNum == f or pointNum == 0:
                return "fp"

        for f in range(len(fixedPoints)):
            if pointNum < fixedPoints[f]:
                depSeq[f] += 1
        point = rotatePoint(point)

    return depSeq


def countDeploymentSequences(deploymentSequences):
    depSeqCount = []

    for ds in deploymentSequences:
        new = 1
        if ds != "fp":
            for sc in depSeqCount:
                if ds == sc[0]:
                    sc[1] += 1
                    new = 0
            if new:
                depSeqCount.append([ds, 1])

    return depSeqCount


def listDeploymentSequences(orbits, base):
    depSeqs = []
    for i in range(len(orbits)):
        depSeqs.append(deploymentSequence(orbits[i], base))
    return depSeqs


# returns a full orbit in spacial order
def fullOrbits(point):
    p = point[:]
    fOrbit = []
    sOrbit = []
    tOrbit = []
    for i in range(len(point)):
        p = rotatePoint(p)
        fOrbit += [p]
    flOrbit = [flattenPoint(fo) for fo in fOrbit]
    flOrbit = quicksort(flOrbit)
    for fl in flOrbit:
        for f in fOrbit:
            if fl == flattenPoint(f):
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


def isRotational(Point: list):
    fullOrbit = fullOrbits(Point)
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


def main():
    D = 3
    Q = 3
    # new = isNewOrbit([2,1,0,0],[[0,2,1,0]])
    # print(new)
    # orbits = listOrbits(D,Q)
    # print(orbits)
    # print(len(orbits))
    o = [0, 0, 0, 0, 1]
    print(fullOrbits(o))
    print(isRotational(o))
    return


if __name__ == "__main__":
    # sys.argv = ["programName.py","--input","test.txt","--output","tmp/test.txt"]
    main()

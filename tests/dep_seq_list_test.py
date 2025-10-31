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


def list_deployment_sequences(orbits):
    depSeqs = []
    for orbit in orbits:
        depSeqs.append(orbit.deployment_sequence())
    return depSeqs


def test_list_dep_seq():
    assert list_deployment_sequences(list_orbits(3, 5), 3) == [
        "fp",
        [5, 5],
        [4, 5],
        [5, 5],
        [3, 5],
        [4, 5],
        [3, 5],
        [5, 5],
        [4, 5],
        [5, 5],
        [2, 5],
        [3, 5],
        [2, 5],
        [4, 5],
        [3, 5],
        [4, 5],
        [2, 5],
        [3, 5],
        [2, 5],
        [5, 5],
        [3, 5],
        [4, 5],
        [3, 5],
        [4, 5],
        [5, 5],
        [1, 5],
        [2, 5],
        [1, 5],
        [2, 5],
        [3, 5],
        [1, 5],
        [2, 5],
        [1, 5],
        [3, 5],
        [2, 5],
        [4, 5],
        [1, 5],
        [2, 5],
        [1, 5],
        [3, 5],
        [1, 5],
        [2, 5],
        [1, 5],
        "fp",
        [0, 5],
        [0, 5],
        [0, 5],
        [0, 5],
        [0, 5],
        [0, 5],
        "fp",
    ]


def test_countDepSeq():
    assert count_deployment_sequences(
        list_deployment_sequences(list_orbits(3, 5), 3)
    ) == [
        [[5, 5], 6],
        [[4, 5], 8],
        [[3, 5], 10],
        [[2, 5], 10],
        [[1, 5], 8],
        [[0, 5], 6],
    ]

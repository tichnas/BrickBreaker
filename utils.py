import numpy as np


def get_representation(representation):
    arr = representation.split("\n")
    maxlen = len(max(arr, key=len))

    return np.array([list(x + (' ' * (maxlen - len(x)))) for x in arr])

import numpy as np
from .pieces import MASKS


def seven_bag(seed):
    rng = np.random.default_rng(seed)
    while True:
        yield from map(str, rng.permutation(list(MASKS)))

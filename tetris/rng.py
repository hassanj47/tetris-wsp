import numpy as np
from .pieces import SPAWN

def bag(seed):
    rng = np.random.default_rng(seed)
    while True:
        yield from rng.permutation(list(SPAWN)).tolist()

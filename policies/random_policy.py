import numpy as np


def random_policy(seed):
    rng = np.random.default_rng(seed)
    def choose(moves):
        # A one-hot preference records the uniformly sampled action.
        scores = np.zeros(len(moves))
        scores[rng.integers(len(moves))] = 1
        return scores, None
    return choose

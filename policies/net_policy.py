import numpy as np
from net.mlp import encode, forward, strongest


def neural(weights, record=False):
    def choose(moves):
        x = encode(moves)
        h1, h2, scores = forward(x, weights)
        trace = None
        if record:
            index = int(np.argmax(scores))
            layers = [layer[index] for layer in (x, h1, h2)]
            trace = dict(layers=[v.tolist() for v in layers],
                         edges=[strongest(v, weights[f"W{i}"]) for i, v in enumerate(layers, 1)])
        return scores, trace
    return choose

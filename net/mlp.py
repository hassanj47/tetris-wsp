import numpy as np


def encode(moves):
    x = np.zeros((len(moves), 205), dtype=np.float32)
    for i, move in enumerate(moves):
        x[i, :200] = move.board.ravel() != 0
        x[i, 200 + len(move.rows)] = 1
    return x


def forward(x, w):
    with np.errstate(over="raise", invalid="raise"):
        h1 = np.maximum(0, x @ w["W1"] + w["b1"])
        h2 = np.maximum(0, h1 @ w["W2"] + w["b2"])
        y = h2 @ w["W3"] + w["b3"]
    return h1, h2, y[:, 0]


def strongest(values, weights, limit=24):
    contributions = values.astype(np.float64)[:, None] * weights
    indices = np.argsort(-np.abs(contributions).ravel(), kind="stable")[:limit]
    edges = []
    for flat in indices:
        i, j = np.unravel_index(flat, weights.shape)
        if contributions[i, j]:
            edges.append([int(i), int(j), float(weights[i, j]), float(contributions[i, j])])
    return edges

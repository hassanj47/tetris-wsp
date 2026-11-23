"""Direct construction from the board and scoring specification alone."""
import numpy as np

from author.weight_io import SHAPES, destination, save


def build():
    w = {name: np.zeros(shape, dtype=np.float32) for name, shape in SHAPES.items()}
    assert sum(a.size for a in w.values()) == 30529 and all(not a.any() for a in w.values())
    first, second, output = w['W1'], w['W2'], w['W3']
    # A filled cell immediately above an empty cell starts an inaccessible gap.
    for row in range(9, 19):
        for col in range(10):
            unit = (row - 9) * 10 + col
            cell = row * 10 + col
            first[cell, unit] = 1
            first[cell + 10, unit] = -1
            second[unit, 0] = 1
    output[0] = -14

    # Neighboring column loads approximate landing heights on compact boards.
    for col in range(10):
        first[col:200:10, 100 + col] = 1
    for left in range(9):
        positive, negative = 1 + 2 * left, 2 + 2 * left
        second[100 + left:102 + left, positive] = [1, -1]
        second[100 + left:102 + left, negative] = [-1, 1]
        output[positive:negative + 1] = -1

    # Growth near spawn consumes scarce headroom. A rising marginal cost
    # favors placing cells low even when two options create equal roof counts.
    for row in range(20):
        altitude = 19 - row
        first[10 * row:10 * row + 10, 110] = altitude + max(0, altitude - 7) * 3
    second[110, 19] = 1
    output[19] = -0.25
    first[200:205, 111] = [0, 2, 6, 10, 16]
    second[111, 20] = 1
    output[20] = 1
    return w


if __name__ == '__main__':
    save(destination('weights/v3_initial.npz'), build())

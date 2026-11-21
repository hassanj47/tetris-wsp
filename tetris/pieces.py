"""Spawn masks viewed from above the board. Rotate clockwise, then trim."""
import numpy as np

SPAWN = dict(I=["1111"], O=["11","11"], T=["010","111"], S=["011","110"],
             Z=["110","011"], J=["100","111"], L=["001","111"])

def rotations(rows):
    mask = np.array([[int(c) for c in row] for row in rows])
    shapes = []
    for _ in range(4):
        cells = tuple(zip(*np.nonzero(mask), strict=True))
        if cells not in shapes:
            shapes.append(cells)
        mask = np.rot90(mask, -1)
    return shapes

SHAPES = {name: rotations(rows) for name, rows in SPAWN.items()}
IDS = {name: i for i, name in enumerate(SPAWN, 1)}

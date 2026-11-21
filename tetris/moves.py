from dataclasses import dataclass
import numpy as np
from .pieces import IDS, SHAPES

@dataclass
class Placement:
    rotation: int
    x: int
    y: int
    board: np.ndarray
    rows: list
    cells: list

def placements(board, piece):
    # The first collision in each covered column bounds the vertical descent.
    tops = np.where(board.any(axis=0), (board != 0).argmax(axis=0), 20)
    for rotation, shape in enumerate(SHAPES[piece]):
        width = 1 + max(c for _, c in shape)
        for x in range(11-width):
            y = int(min(tops[x+c]-r-1 for r,c in shape))
            if y < 0:
                continue
            cells = [(int(y+r), int(x+c)) for r,c in shape]
            locked = board.copy()
            for r,c in cells:
                locked[r,c] = IDS[piece]
            full = locked.all(axis=1)
            rows = np.flatnonzero(full).tolist()
            if rows:
                locked = np.vstack((np.zeros((len(rows),10), np.uint8), locked[~full]))
            yield Placement(rotation, x, y, locked, rows, cells)

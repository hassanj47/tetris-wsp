from dataclasses import dataclass
import numpy as np
from .pieces import IDS, SHAPES


@dataclass
class Placement:
    rotation: int
    x: int
    y: int
    rows: list
    board: np.ndarray


def placements(board, piece):
    occupied = board != 0
    # First occupied row per column, including the floor sentinel.
    ceiling = np.where(occupied.any(axis=0), occupied.argmax(axis=0), 20)
    moves = []
    for rotation, shape in enumerate(SHAPES[piece]):
        dx, dy = np.array(shape).T
        for x in range(10 - int(dx.max())):
            columns = x + dx
            y = int((ceiling[columns] - dy - 1).min())
            if y < 0:
                continue
            after = board.copy()
            after[y + dy, columns] = IDS[piece]
            full = after.all(axis=1)
            rows = np.flatnonzero(full).tolist()
            if rows:
                after = np.vstack((np.zeros((len(rows), 10), dtype=np.uint8), after[~full]))
            moves.append(Placement(rotation, x, y, rows, after))
    return moves

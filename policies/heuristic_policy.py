import numpy as np


def heuristic(moves):
    boards = np.stack([move.board for move in moves]) != 0
    heights = np.where(boards.any(axis=1), 20 - boards.argmax(axis=1), 0)
    holes = heights.sum(axis=1) - boards.sum(axis=(1, 2))
    roughness = np.abs(np.diff(heights, axis=1)).sum(axis=1)
    lines = np.array([len(move.rows) for move in moves])
    scores = -.510066 * heights.sum(axis=1) + .760666 * lines - .35663 * holes - .184483 * roughness
    return scores, None

import numpy as np
from .moves import placements
from .rng import seven_bag


def play(seed, cap, choose):
    """Yield committed moves. The chooser has no access to the bag or future pieces."""
    if not 1 <= cap <= 1000:
        raise ValueError("cap must be between 1 and 1000")
    board = np.zeros((20, 10), dtype=np.uint8)
    bag = seven_bag(seed)
    for _ in range(cap):
        piece = next(bag)
        moves = placements(board, piece)
        if not moves:
            return
        scores, trace = choose(moves)
        if np.shape(scores) != (len(moves),) or not np.isfinite(scores).all():
            raise ValueError("expected one finite score per legal placement")
        selected = int(np.argmax(scores))
        yield board, piece, moves, scores, selected, trace
        board = moves[selected].board

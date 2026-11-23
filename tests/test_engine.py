from itertools import islice
import numpy as np
import pytest
from tetris.moves import placements
from tetris.pieces import SHAPES
from tetris.rng import seven_bag
from tetris.engine import play
from policies.random_policy import random_policy


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_line_clears_at_right_wall(count):
    board = np.zeros((20, 10), np.uint8)
    board[-count:, :-1] = 1
    move = next(m for m in placements(board, "I") if m.rotation == 1 and m.x == 9)
    assert move.y == 16 and len(move.rows) == count
    assert np.count_nonzero(move.board) == 4-count
    assert board[-1, 9] == 0


def test_rotations_order_and_topout():
    assert [len(v) for v in SHAPES.values()] == [2, 1, 4, 2, 2, 4, 4]
    board = np.zeros((20, 10), np.uint8)
    assert [m.x for m in placements(board, "O")] == list(range(9))
    for piece in SHAPES:
        moves = [(m.rotation, m.x) for m in placements(board, piece)]
        assert moves == sorted(set(moves))
    board[0] = 1
    assert not placements(board, "T")


def test_repeatability_and_bags():
    pieces = list(islice(seven_bag(42), 70))
    assert pieces == list(islice(seven_bag(42), 70))
    assert all(set(pieces[i:i+7]) == set(SHAPES) for i in range(0, 70, 7))
    def run():
        return [(p, i, m[i].board.tobytes()) for _, p, m, _, i, _ in play(9, 1000, random_policy(9))]
    assert run() == run()
    assert len(run()) < 1000


def test_tie_break():
    assert next(play(0, 1, lambda moves: (np.ones(len(moves)), None)))[4] == 0

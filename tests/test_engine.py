import unittest
from itertools import islice
import numpy as np
from tetris.engine import Game
from tetris.moves import placements
from tetris.rng import bag
from tetris.pieces import SHAPES

class EngineTests(unittest.TestCase):
    def test_clear_counts_and_rightmost_drop(self):
        for n in range(1,5):
            board = np.zeros((20,10),np.uint8)
            board[-n:,:9] = 2
            move = next(m for m in placements(board,'I') if m.x==9)
            self.assertEqual(move.rows,list(range(20-n,20)))
            self.assertEqual(np.count_nonzero(move.board),4-n)
            self.assertEqual(move.y,16)
            self.assertEqual(np.count_nonzero(board),9*n)

    def test_rotations_order_and_topout(self):
        self.assertEqual([len(v) for v in SHAPES.values()],[2,1,4,2,2,4,4])
        board = np.zeros((20,10),np.uint8)
        self.assertEqual([m.x for m in placements(board,'O')],list(range(9)))
        for piece in SHAPES:
            keys=[(m.rotation,m.x) for m in placements(board,piece)]
            self.assertEqual(keys,sorted(set(keys)))
        board[0]=1
        self.assertFalse(list(placements(board,'T')))

    def test_bags_and_games(self):
        seq=list(islice(bag(91),70))
        self.assertEqual(seq,list(islice(bag(91),70)))
        for i in range(0,70,7):
            self.assertEqual(set(seq[i:i+7]),set(SHAPES))
        a,b=Game(91,5),Game(91,5)
        with self.assertRaises(ValueError): a.step(-1)
        while a.moves:
            a.step(0)
            b.step(0)
            np.testing.assert_array_equal(a.board,b.board)
        self.assertEqual(a.pieces,5)
        self.assertFalse(b.moves)

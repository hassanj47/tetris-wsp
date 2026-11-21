import numpy as np
from net.mlp import encode, forward
from net.spec import load, digest

def heuristic(move):
    board = move.board != 0
    heights = np.where(board.any(axis=0),20-board.argmax(axis=0),0)
    holes = np.count_nonzero(np.maximum.accumulate(board,axis=0) & ~board)
    return (-0.510066*heights.sum() + 0.760666*len(move.rows)
            - 0.35663*holes - 0.184483*np.abs(np.diff(heights)).sum())

class Policy:
    def __init__(self, kind, seed, path=None, version=None):
        if kind not in ("random","heuristic","neural"):
            raise ValueError("unknown policy")
        if (kind == "neural") != bool(path):
            raise ValueError("supply weights for neural policies only")
        self.kind = kind
        self.rng = np.random.default_rng(np.random.SeedSequence([seed,1]))
        self.weights = load(path) if path else None
        self.meta = dict(kind=kind,version=version or kind,artifact=str(path) if path else None,
                         sha256=digest(path) if path else None)

    def decide(self,moves):
        layers = None
        if self.kind == "random":
            # IID continuous priorities give a uniform choice.
            scores = self.rng.random(len(moves))
        elif self.kind == "heuristic":
            scores = np.array([heuristic(m) for m in moves])
        else:
            scores,layers = forward(encode(moves),self.weights)
        return int(np.argmax(scores)),scores,layers

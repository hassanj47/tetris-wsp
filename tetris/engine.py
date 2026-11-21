import numpy as np
from .rng import bag
from .moves import placements

class Game:
    def __init__(self, seed, cap=1000):
        if not 1 <= cap <= 1000:
            raise ValueError("piece cap must be between 1 and 1000")
        self.board = np.zeros((20,10), np.uint8)
        self.stream = bag(seed)
        self.cap = cap
        self.pieces = 0
        self.piece = next(self.stream)
        self.moves = list(placements(self.board, self.piece))

    def step(self, index):
        if not 0 <= index < len(self.moves):
            raise ValueError("illegal candidate index")
        self.board = self.moves[index].board
        self.pieces += 1
        self.piece = next(self.stream)
        self.moves = list(placements(self.board, self.piece)) if self.pieces < self.cap else []

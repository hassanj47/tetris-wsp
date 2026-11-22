# WSP Author Brief — Tetris Placement-Scoring Network

This brief is the complete task specification for the isolated WSP Author session. It intentionally excludes baseline implementations, baseline coefficients, and performance results.

## 1. Task

Construct a neural network that chooses among legal placements in the simplified Tetris environment described below.

The network scores a candidate post-placement board. The game engine generates legal placements and executes the highest-scoring candidate.

The objective is to create the network weights directly through reasoning and deterministic numerical construction. Do not train the network.

## 2. Game rules

- Board: 20 rows × 10 columns.
- Seven tetrominoes: I, O, T, S, Z, J, L.
- Fixed, documented shape coordinates and unique rotations.
- Seven-bag randomizer.
- Current piece only; no hold and no next-piece preview.
- Enumerate legal `(rotation_index, x)` placements.
- Hard-drop each candidate vertically, lock it, and clear complete rows.
- No spins, tucks, or horizontal movement after descent.
- No wall-kick system is required.
- Game ends when no legal placement exists.
- Maximum 1,000 placed pieces per game.
- Candidate ordering: `(rotation_index, x)` ascending.
- Equal scores are resolved by choosing the lowest candidate index.

The environment is a simplified placement-based Tetris variant, not a complete implementation of modern guideline Tetris.

## 3. Policy

For each legal candidate:
1. simulate its resulting board after hard drop, lock, and line clear;
2. encode that resulting board;
3. pass the encoded candidate to the network;
4. receive one scalar score;
5. choose the candidate with the highest score.

The network does not output keyboard actions, rotations, or coordinates directly.

## 4. Input encoding

Input is a float32 vector of exactly 205 values.

- `x[0:200]`: flattened post-placement board, row-major, top-to-bottom and left-to-right. Empty = 0, occupied = 1.
- `x[200:205]`: one-hot encoding of lines cleared by the candidate:
  - 0 lines;
  - 1 line;
  - 2 lines;
  - 3 lines;
  - 4 lines.

## 5. Fixed network architecture

```python
h1 = relu(x  @ W1 + b1)   # W1: (205, 128), b1: (128,)
h2 = relu(h1 @ W2 + b2)   # W2: (128, 32),  b2: (32,)
y  =       h2 @ W3 + b3   # W3: (32, 1),    b3: (1,)
```

The output is one scalar score. Higher scores are preferred.

Total parameters: 30,529.

The architecture and shapes are fixed and must not be changed.

## 6. Artifact format

Create a NumPy `.npz` file containing:
- `W1`: float32 `(205, 128)`
- `b1`: float32 `(128,)`
- `W2`: float32 `(128, 32)`
- `b2`: float32 `(32,)`
- `W3`: float32 `(32, 1)`
- `b3`: float32 `(1,)`

All values must be finite. The artifact must be deterministic and reproducible from the submitted authoring script.

## 7. Required Author outputs

- deterministic `build_v1.py`;
- `v1.npz`;
- `v1_labels.json` with intended neuron roles or hypotheses;
- a log explaining the construction method and design decisions;
- artifact provenance and hashes.

Do not execute the game or policy during the initial attempt. Do not train, optimize, search, or use gradient-based methods.

Read `RULES.md` for the complete authoring protocol.

## Implemented orientation and placement convention

Spawn masks below use dots for empty cells and slashes between rows. Rotation 0 is the listed mask. Subsequent indices rotate clockwise in screen coordinates, normalize the minimum x and y to zero, and omit duplicates. x is the leftmost occupied column of that normalized mask. A candidate must fit fully on the board at row zero and descend vertically from above the stack.

| Piece | Spawn mask |
|---|---|
| I | IIII |
| O | OO/OO |
| T | .T./TTT |
| S | .SS/SS. |
| Z | ZZ./.ZZ |
| J | J../JJJ |
| L | ..L/LLL |

## Evaluation measures

Final reporting includes lines, pieces survived, clear counts by size, cap frequency, mean and maximum stack height, and the fraction of committed boards with column 9 empty. Stack height is the distance from the floor to the highest occupied cell. Tetrises per game, share of clear events that are Tetrises, and share of lines cleared by Tetrises have distinct denominators. Candidate scoring receives only the specified 205 inputs.

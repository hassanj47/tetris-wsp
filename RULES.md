# RULES.md — WSP Authoring and Editing Protocol

These rules apply to the separate Astra Author (v1) and Editor (v2) sessions.

## 1. Objective

Construct or directly modify the fixed neural network weights for the Tetris placement-scoring policy described in `author_brief/BRIEF.md`.

This is weight-space programming, not conventional model training.

## 2. Prohibited methods

Do not use:
- gradient descent or backpropagation;
- optimizers;
- training loops;
- evolutionary algorithms;
- random search over weights;
- candidate-weight search loops;
- reinforcement learning;
- supervised fitting;
- external pretrained neural models to generate or replace the specified controller;
- repeated game execution to optimize weights during the initial attempt.

Do not call the game engine or evaluation tools during the initial authoring attempt.

## 3. Permitted methods

You may:
- reason from the game rules and network specification;
- write deterministic Python/NumPy scripts to construct the tensors;
- use analytically chosen or hand-designed numerical values;
- inspect tensor values, shapes, sparsity, and finite-value checks;
- document intended neuron roles and strategy hypotheses;
- create a human-readable dump of the generated weights;
- save architecture and provenance metadata.

## 4. Fixed architecture

The architecture is immutable:

```python
h1 = relu(x  @ W1 + b1)   # W1: (205, 128), b1: (128,)
h2 = relu(h1 @ W2 + b2)   # W2: (128, 32),  b2: (32,)
y  =       h2 @ W3 + b3   # W3: (32, 1),    b3: (1,)
```

Total parameters: 30,529.

Use float32 arrays and exact tensor names and shapes.

## 5. Determinism and validation

- The authoring script must be deterministic.
- Do not rely on unseeded randomness.
- Reject NaN and infinity.
- Validate exact shapes and dtypes.
- Save a reproducibility record describing the script, method, and artifact hashes.
- Do not silently change the architecture or input representation.

## 6. Initial zero-evaluation attempt

The initial attempt must be completed without:
- running Tetris;
- running a policy;
- receiving evaluation scores;
- seeing baseline results;
- observing per-seed trajectories.

Static artifact validation is allowed.

Record the initial attempt in `author/LOG.md`.

## 7. Optional refinement budget

Only if explicitly authorized after the initial artifact:
- maximum three evaluation-feedback iterations;
- each feedback report covers 20 games;
- reports contain aggregate summary statistics only;
- do not expose seed-level trajectories or move-by-move traces;
- log every report and every subsequent artifact revision.

If refinement is used, describe the result as feedback-assisted WSP, not purely zero-shot.

## 8. Editor-specific rules

The Editor must:
- load the exact `v1.npz` artifact;
- preserve all tensor shapes and the architecture;
- make explicit modifications to the existing arrays;
- save the result as `v2.npz`;
- report changed parameter count and percentage;
- provide per-tensor change statistics;
- explain which intended strategy changes the edits implement;
- document any unused neurons repurposed, if applicable.

The Editor must not silently discard v1 and independently generate a new network.

## 9. Required artifacts

### Author
- `author/build_v1.py`
- `weights/v1.npz`
- `weights/v1_labels.json`
- `author/LOG.md`
- provenance metadata and hashes

### Editor
- `author/edit_v2.py`
- `weights/v2.npz`
- `weights/v2_labels.json`
- updated `author/LOG.md`
- parameter-change report

## 10. Reporting honesty

Do not claim:
- the network learned from gameplay;
- the network was trained;
- a neuron has a semantic meaning without evidence;
- a strategy improved without validation;
- a result is zero-shot if feedback or game evaluation influenced weight construction.

Report failures and inconclusive results as valid outcomes.

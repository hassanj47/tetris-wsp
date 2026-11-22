# PLAN.md — Tetris Weight-Space Programming Demo

## 0. Goal

Build a polished, reproducible demonstration in which a neural network plays a simplified, deterministic version of Tetris and its weights are written directly by GPT-6.2 Astra using weight-space programming (WSP).

The experiment has two stages and supports two public-facing stories:

### Experiment 1 — v1: direct weight synthesis

A fresh Astra session writes the complete weight tensors of a fixed neural placement-scoring network using only:
- the implemented game rules,
- the input representation,
- the exact network architecture and tensor shapes,
- the output contract and authoring rules.

The initial attempt must not run the game, receive evaluation feedback, train, use gradients, or search over candidate weights.

### Experiment 2 — v2: direct weight editing

A separate, fresh Astra session receives:
- the original v1 weights,
- the permitted human-readable weight dump and neuron labels,
- the same network specification,
- one natural-language instruction:

> Keep the rightmost column empty and clear lines four at a time (Tetrises).

The Editor must modify the existing weights directly, preserve the architecture and tensor shapes, and report exactly what changed. It must not train or optimize the network.

The experiment succeeds as a WSP demonstration even if v1 or v2 performs imperfectly, provided the process is genuine, reproducible, and honestly reported. Performance improvement is a measured outcome, not a guaranteed claim.

## 1. Product and research deliverables

1. Reproducible GitHub repository.
2. Deterministic Tetris engine and move generator.
3. Fixed NumPy MLP inference implementation.
4. Random and conventional heuristic baselines.
5. Evaluation, replay, weight-dump, rule-check, and weight-diff tools.
6. Polished static browser viewer with two synchronized visual panels.
7. v1 direct-synthesis artifacts and logs.
8. v2 direct-edit artifacts and logs.
9. Reproducible evaluation reports and replay files.
10. Two short LinkedIn demonstration videos.

## 2. Roles and isolation

Use three distinct workspaces or fresh sessions.

| Workspace | Purpose | Permitted access |
|---|---|---|
| Builder | Implement engine, tools, tests, viewer, and documentation | Full repository |
| Author (v1) | Synthesize initial weights | `author_brief/BRIEF.md`, `RULES.md`, and designated output location only |
| Editor (v2) | Modify v1 weights directly | Brief, rules, v1 weights, v1 labels, and permitted v1 weight dump only |

Author and Editor must be fresh Astra sessions. Do not rely on a prompt instruction alone to hide forbidden files: create minimal isolated workspaces containing only the permitted inputs and output directories.

The Builder must stop after the engine, tools, tests, viewer, documentation, and author brief are ready. It must not generate the experimental v1 or v2 weights.

## 3. Honesty and evaluation policy

### 3.1 Initial zero-evaluation attempts

The initial v1 and v2 authoring attempts are zero-evaluation attempts:
- no running the game or policy before producing the initial artifact;
- no game outcomes or baseline results supplied to the Author or Editor;
- no training, gradient descent, optimizers, random search, evolutionary search, or tuning loops.

Static tensor inspection and deterministic shape/finite-value validation are allowed.

### 3.2 Optional refinement

If the initial result is weak, optional feedback-assisted refinement is allowed only under this explicit budget:

- maximum three feedback iterations per experiment;
- each feedback report covers 20 games;
- feedback contains summary statistics only, not per-seed trajectories or move-by-move traces;
- every report and subsequent weight revision is recorded in the experiment log.

Any experiment using this refinement must be described as feedback-assisted WSP, not as a purely zero-shot result.

### 3.3 Final validation

After authoring is complete:
- evaluate v1 on a fixed 100-seed validation set;
- evaluate v2 on exactly the same 100 seeds;
- keep the final validation results withheld from Author and Editor until their initial artifacts are complete;
- publish aggregate statistics and disclose any prior feedback iterations.

Use a separate seed range for optional refinement so the final validation set remains held out.

## 4. Repository structure

```text
tetris-wsp/
  README.md
  PLAN.md
  AGENTS.md
  CODEX_BUILDER_TASK.md
  RULES.md
  requirements.txt
  pyproject.toml
  .gitignore

  tetris/
    __init__.py
    pieces.py
    engine.py
    moves.py
    rng.py

  net/
    __init__.py
    mlp.py
    spec.py

  policies/
    __init__.py
    net_policy.py
    heuristic_policy.py
    random_policy.py

  tools/
    eval.py
    record.py
    dump_weights.py
    check_rules.py
    diff_weights.py

  viewer/
    index.html
    viewer.css
    viewer.js
    data/
      manifest.json

  author_brief/
    BRIEF.md

  author/
    README.md
    LOG.md

  weights/
    README.md
    dumps/
      README.md

  results/
    README.md

  replays/
    README.md

  tests/
```

Do not commit generated v1/v2 weights until the corresponding authoring experiment has actually occurred. Do not fabricate sample results or transcripts.

## 5. Tetris rules and deterministic engine

Keep the game simple, deterministic, and fully specified.

### Board
- 20 rows × 10 columns.
- Row 0 is the top; column 0 is the left.
- Board is represented as `numpy.uint8` with shape `(20, 10)`.
- Empty cells are 0; occupied cells are 1 or a documented piece identifier.

### Pieces
Use the seven tetrominoes: I, O, T, S, Z, J, L.
- Use fixed, documented shape coordinates.
- Deduplicate identical rotations.
- O has one unique rotation.
- I, S, and Z have two unique rotations.
- T, J, and L have four unique rotations.

### Randomizer
- Seven-bag piece sequence.
- Use `numpy.random.default_rng(seed)`.
- Same seed and configuration must always produce the same piece sequence.

### Move generation
For the current piece:
- enumerate every legal `(rotation_index, x)` placement;
- hard-drop the piece vertically to the lowest legal position;
- lock the piece;
- clear all completed rows;
- do not implement hold, next-piece preview, spins, tucks, or horizontal movement after descent;
- no wall-kick system is required for this simplified placement environment.

The game is a deliberately simplified placement-based Tetris variant. The UI may animate the falling piece and hard drop, but the policy chooses a final legal placement.

### Game over and cap
- Game ends when no legal placement exists for the next piece.
- Default cap: 1,000 placed pieces per game.
- The cap prevents pathological endless games.

### Candidate ordering and tie-breaking
- Candidate ordering is deterministic: `(rotation_index, x)` ascending.
- If candidate scores are exactly equal, select the lowest candidate index.

### Required engine tests
- single, double, triple, and four-line clears;
- vertical I-piece placement in column 9;
- O-piece has exactly nine legal horizontal placements on an empty board;
- duplicate rotations are removed;
- same seed gives the same piece sequence and game;
- game-over detection;
- deterministic candidate ordering and tie-breaking.

## 6. Neural network specification

### 6.1 Policy type

The network is a **placement-scoring policy**, not a keyboard-control policy.

For each current piece:
1. Generate every legal rotation and horizontal placement.
2. Simulate the resulting hard drop, lock, and line clear.
3. Encode the resulting post-placement board.
4. Evaluate the candidate board with the MLP.
5. Select the legal placement with the highest scalar score.

The engine handles legal moves and game mechanics. The neural network decides which candidate placement is preferred.

### 6.2 Input vector: 205 float32 values

- `x[0:200]`: flattened resulting board, row-major, top to bottom, left to right; binary occupancy values.
- `x[200:205]`: one-hot encoding of the number of lines cleared by this placement:
  - index 0: zero lines;
  - index 1: one line;
  - index 2: two lines;
  - index 3: three lines;
  - index 4: four lines.

The input is based on the board after the candidate placement has locked and completed rows have been removed.

### 6.3 Fixed architecture

```python
h1 = relu(x  @ W1 + b1)   # W1: (205, 128), b1: (128,)
h2 = relu(h1 @ W2 + b2)   # W2: (128, 32),  b2: (32,)
y  =       h2 @ W3 + b3   # W3: (32, 1),    b3: (1,)
```

Output is one scalar placement score. Higher is better.

Total parameters:

- W1: 26,240
- b1: 128
- W2: 4,096
- b2: 32
- W3: 32
- b3: 1
- **Total: 30,529 parameters**

### 6.4 Weight artifact

`weights/v1.npz` and `weights/v2.npz` contain:
- `W1`, `b1`, `W2`, `b2`, `W3`, `b3`;
- float32 arrays;
- exact shapes above;
- finite values only (reject NaN and infinity).

Store architecture metadata and provenance separately in JSON. Do not silently cast malformed shapes or hide invalid values.

### 6.5 Neuron labels

Store labels in `weights/v1_labels.json` and `weights/v2_labels.json`.

Labels may describe intended roles or hypotheses. Do not present an intended label (for example, "hole detector") as a proven neuron interpretation unless supported by an actual analysis.

## 7. WSP authoring rules

The Author and Editor must follow `RULES.md`.

Key restrictions:
- no training of any kind;
- no gradients or optimizers;
- no random/evolutionary search;
- no candidate-weight search loops;
- no game execution during the initial authoring attempt;
- deterministic artifact creation;
- exact architecture and tensor shapes;
- all reasoning, scripts, changes, and evaluation feedback logged.

The Author may write deterministic NumPy code to construct the weight arrays. The Editor must load and modify the existing v1 weights rather than silently replacing them with a new independently generated network.

## 8. Baselines

Implement two comparison policies that are unavailable to the Author and Editor.

### Random policy
Chooses uniformly among legal placements using a seeded RNG.

### Conventional heuristic policy
Use a documented conventional Tetris heuristic based on:
- aggregate column height;
- completed lines;
- holes;
- surface bumpiness.

Keep its implementation and coefficients outside `author_brief/`.

The baselines are for contextual evaluation only. Do not make beating the heuristic the primary WSP success criterion. Report all results honestly.

## 9. Evaluation and metrics

Implement `tools/eval.py`.

Per game, record:
- lines cleared;
- pieces placed;
- Tetrises (four-line clears);
- singles, doubles, and triples;
- whether the 1,000-piece cap was reached;
- mean stack height;
- maximum stack height;
- fraction of post-placement boards where column 9 is entirely empty.

Aggregate:
- mean, median, minimum, and maximum lines cleared;
- mean pieces placed;
- mean Tetrises per game;
- line-clear event composition;
- percentage of games reaching the piece cap;
- mean column-9-empty fraction.

### Strategy-specific metrics

For v2, report:
- `column_9_empty_fraction`: fraction of post-placement boards where all 20 cells in column 9 are empty;
- `tetrises_per_game`: average four-line clears per game;
- `tetris_event_share`: four-line clears divided by all line-clear events;
- `tetris_line_share`: lines cleared via four-line clears divided by all lines cleared;
- survival: mean pieces placed.

Do not use an ambiguous single "Tetris rate" without defining its denominator.

### v2 success interpretation

The intended strategy is to preserve column 9 as a vertical well and use I-pieces to clear four lines. The evaluation should show whether the modified network actually does this.

Report both the intended-strategy metrics and survival. Do not declare v2 successful solely because it keeps the well empty if it dies substantially earlier or fails to produce more Tetrises.

A lack of improvement is a valid experimental result.

## 10. Tooling requirements

### `tools/eval.py`
- evaluates policies across supplied seeds;
- emits per-game results and aggregate JSON/Markdown reports;
- supports random, heuristic, and neural policies;
- records the exact policy artifact and configuration used.

### `tools/record.py`
Records a deterministic replay containing:
- metadata, seed, and configuration;
- board state before and after each move;
- current piece;
- legal candidate placements;
- candidate scores;
- selected candidate;
- lines cleared and cumulative metrics;
- actual neural activations for the selected candidate;
- network version and weight-artifact identifier.

Store full activation vectors when practical. If the replay is intentionally compact, preserve enough actual values to animate the network accurately and document any aggregation. Never invent activations.

### `tools/dump_weights.py`
Produces a human-readable dump for the Editor:
- tensor shapes and parameter count;
- biases and compact weight summaries;
- first-layer neuron input-weight summaries;
- first-layer board-weight grids where useful;
- neuron labels and stated hypotheses;
- sparse summaries of W2 and W3.

### `tools/check_rules.py`
Statically checks authoring scripts for forbidden imports and obvious prohibited operations. It is a guardrail, not a security sandbox. Record that limitation.

### `tools/diff_weights.py`
Compares v1 and v2:
- changed parameter count;
- percentage changed;
- per-tensor changes;
- largest changed neurons;
- optional visual diff artifact.

## 11. Runtime, replay, and deployment architecture (mandatory)

### 11.1 Core principle

The project is cloud-first.

All Python execution, neural inference, weight generation, game evaluation, and replay generation happen in Codex Cloud.

The user's computer is not required for development, simulation, neural inference, or hosting.

The browser renders and replays the finished demonstration.

No backend server, database, GPU, paid API, or runtime external service is required.

### 11.2 Development and neural execution — Codex Cloud

Use Codex Cloud for:
- implementing and testing the Tetris engine;
- generating v1/v2 weights in separate Astra sessions;
- executing the NumPy neural network;
- evaluating policies;
- recording replays and activations;
- producing reports and visualization data.

The Builder phase itself must not generate experimental v1/v2 weights.

### 11.3 Replay artifacts

The Python simulation produces deterministic, self-contained replay files.

Each replay must include enough data for the browser to reproduce the demonstration without rerunning Python:
- game configuration and seed;
- board states and pieces;
- candidate placements and their scores;
- selected placement;
- line clears and cumulative statistics;
- actual recorded neural activations for the selected decision;
- network version and experiment metadata.

Store full simulation outputs under `replays/`. Copy selected, size-appropriate public replays into `viewer/data/` with a manifest.

Keep weight artifacts separately under `weights/`.

### 11.4 Browser viewer

Build a static application using HTML, CSS, JavaScript, Canvas, and SVG.

No frontend framework is required unless the Builder demonstrates a concrete benefit.

The viewer loads replay files and renders them without Python, a backend, a running Codex session, or runtime API calls.

### 11.5 Two-panel visualization

**Left: Tetris gameplay**
- board and tetrominoes;
- current and ghost/selected placement;
- top candidate placements where useful;
- score, lines, Tetrises, and pieces placed;
- playback controls and speed selection.

**Right: neural network**
- sleek, modern animated neural-network visualization as the default;
- clear input, hidden, and output layers;
- abstract the 205 inputs so the display remains legible;
- represent the 128- and 32-neuron hidden layers faithfully;
- animate actual recorded activations;
- highlight selected weighted contributions using actual weights and activations;
- show the selected candidate's score;
- provide a secondary weight-inspection view.

The visual direction should be inspired by the mathematical clarity and explanatory motion of 3Blue1Brown/Manim-style explainers, without copying assets, branding, or exact compositions.

**Neural network first; heatmap second.** Do not use raw Matplotlib or Seaborn output as the main interface. A compact, carefully styled weight view is optional and subordinate to the animated network.

The network visualization must correspond to the actual architecture, weights, and recorded inference. Do not use decorative activity disconnected from the model.

### 11.6 Comparison mode

Support synchronized v1/v2 replay comparison:
- both boards visible;
- same seed and game configuration;
- synchronized playback;
- relevant strategy metrics;
- changed-weight percentage;
- clear indication of which network is being shown.

### 11.7 GitHub Pages

Deploy the static viewer from `viewer/` using GitHub Actions.

Requirements:
- no backend;
- no runtime API calls;
- no authentication;
- no database;
- no active Codex session required;
- direct loading through the GitHub Pages URL must work.

The repository owner must enable GitHub Pages if required by repository settings. Confirm repository visibility and Pages eligibility before claiming deployment success.

## 12. Viewer design requirements

The viewer must feel like a polished product demo, not a debug dashboard.

### Design language
- dark, restrained visual system;
- crisp typography and clear hierarchy;
- deliberate spacing;
- smooth, purposeful motion;
- legible at 1920×1080 screen-recording resolution;
- responsive enough to inspect at smaller widths.

### Default screen
- left panel: Tetris gameplay;
- right panel: animated neural network;
- concise status: "Astra WSP brain", "No training", network version;
- synchronized replay controls.

### Neural visualization behavior
When a candidate is evaluated:
1. show the candidate input/board representation;
2. animate actual layer activations;
3. emphasize selected weighted contributions;
4. display the scalar output score;
5. highlight the chosen placement in the Tetris panel.

Use actual replay data. If a particular internal signal is not recorded, do not fabricate it.

### Secondary views
- Feature view: board occupancy, line-clear one-hot inputs, and candidate scores.
- Weight view: compact first-layer receptive-field grids or selected tensor summaries.
- v1/v2 compare view: synchronized boards and metrics.

## 13. Author brief

`author_brief/BRIEF.md` must be self-contained and include only:
1. implemented game rules;
2. policy and candidate evaluation procedure;
3. exact input encoding;
4. fixed architecture and tensor shapes;
5. weight file format;
6. required output artifacts;
7. evaluation metrics that will eventually be reported;
8. pointer to `RULES.md`.

It must not contain:
- heuristic implementation or coefficients;
- baseline results;
- Builder's private reasoning;
- v1/v2 performance results;
- hidden validation seeds.

## 14. Implementation phases and acceptance criteria

### Phase 1 — Builder: engine and baselines
- implement deterministic Tetris engine and move generation;
- implement randomizer and seed handling;
- implement tests;
- implement NumPy MLP runtime and architecture validation;
- implement random and heuristic baselines.

Acceptance:
- tests pass;
- game and candidate generation are deterministic;
- random and heuristic policies run;
- heuristic baseline is not catastrophically broken;
- architecture and shape checks work.

### Phase 2 — Builder: tools and viewer
- implement evaluation and reporting;
- implement replay recording;
- implement weight dump and diff tools;
- implement authoring-rule checker;
- implement static two-panel viewer;
- implement neural visualization using actual replay activations;
- implement v1/v2 compare mode;
- write complete author brief and documentation;
- add GitHub Pages workflow.

Acceptance:
- baseline replay opens in viewer;
- a test fixture with clearly identified synthetic/mock weights is used only to test visualization before real WSP weights exist;
- synthetic fixture data is never presented as a real Astra-generated result;
- network visualization is animated and reflects the supplied test fixture;
- compare mode works with clearly labeled fixture replays;
- static site builds and deploys;
- all tests pass.

**Builder stops here.** Do not generate v1 or v2 experimental weights.

### Phase 3 — Author: v1 direct synthesis
Fresh Astra session with isolated author workspace.

Outputs:
- `author/build_v1.py`;
- `weights/v1.npz`;
- `weights/v1_labels.json`;
- `author/LOG.md`;
- reproducibility metadata.

Initial attempt must have zero game evaluations.

### Phase 4 — Editor: v2 direct editing
Fresh Astra session with isolated editor workspace.

Instruction:
> Keep the rightmost column empty and clear lines four at a time (Tetrises).

Outputs:
- `author/edit_v2.py`;
- `weights/v2.npz`;
- `weights/v2_labels.json`;
- updated `author/LOG.md`;
- explicit parameter-change report.

The Editor must load and modify v1. It must not silently replace it with a separately authored network.

### Phase 5 — Final evaluation and recording
- validate v1 and v2 on the same held-out 100 seeds;
- evaluate baselines on the same seed set;
- record selected v1/v2 replays;
- generate reports and weight diffs;
- copy selected replay files into `viewer/data/`;
- update manifest;
- deploy GitHub Pages;
- record two videos.

## 15. Video plan

### Video 1 — "This Tetris AI was never trained"
Target: 30–45 seconds.

Sequence:
1. Title: "0 training steps. 30,529 weights written directly by an LLM."
2. Brief glimpse of the Author task and generated artifact.
3. Split-screen gameplay and animated neural network.
4. Show actual candidate scores and chosen move.
5. End with measured v1 performance and a clear WSP explanation.

### Video 2 — "I changed its strategy with one sentence"
Target: 30–45 seconds.

Sequence:
1. Show the natural-language instruction.
2. Show a concise weight-change summary.
3. Show synchronized v1/v2 gameplay on the same seed.
4. Highlight right-column well behavior and four-line clears.
5. End with measured v1-to-v2 metrics.

Do not imply that the network learned from experience or that a strategy change succeeded unless the results demonstrate it.

## 16. Technical stack

- Python 3.11+ (or the compatible version provided by the Codex Cloud environment).
- NumPy.
- pytest.
- Static HTML/CSS/JavaScript.
- Canvas for gameplay.
- SVG or Canvas for neural visualization.
- GitHub Actions and GitHub Pages for static deployment.

No PyTorch, TensorFlow, JAX, GPU, backend, database, or runtime API is required.

## 17. Final success criteria

### Experimental integrity
- v1 weights are directly constructed by Astra;
- v2 is a direct edit of v1;
- no conventional training or gradient descent is used;
- all iterations and feedback are logged;
- final evaluation is reproducible and disclosed.

### Functional
- deterministic engine;
- exact MLP architecture and inference;
- valid weights and activations;
- working baselines and evaluation;
- self-contained replays.

### Visual
- polished two-panel viewer;
- gameplay and network animation synchronized;
- actual activations and decisions shown;
- weight inspection available as a secondary view;
- synchronized v1/v2 comparison;
- GitHub Pages deployment works independently.

### Narrative
A viewer should understand:

"The left side shows Tetris being played. The right side shows the neural network that directly evaluates and chooses placements. Its weights were written by an LLM without conventional training. A second LLM session then modified those weights to change its strategy."

## 18. First execution order

1. Create the GitHub repository.
2. Add this bootstrap and project instructions.
3. Open the repository in Codex Cloud.
4. Select the Astra-capable model and run the Builder task.
5. Review the Builder output and acceptance tests.
6. Stop Builder.
7. Run v1 Author in a fresh isolated Astra session.
8. Run v2 Editor in a separate fresh isolated Astra session.
9. Evaluate, record, publish, and create the two videos.

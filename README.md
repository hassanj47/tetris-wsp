# Tetris WSP · Placement Lab

Placement Lab replays a Tetris game alongside the exact neural decision that selected each placement. The Python simulator and the static browser viewer run independently. The bundled recordings cover two synthetic visualization fixtures and a conventional baseline. The Astra Author and Editor experiments are pending.

## Run the viewer

From the repository root:

```bash
python -m http.server 8000 --directory viewer
```

Open **http://localhost:8000**. Any static web server works. Play, pause, scrub or step through placements. Select Fixture B under **Compare with** to see the same seven-bag sequence under two fixture policies. **Network**, **Features** and **Weights** inspect the primary recording. See [viewer/README.md](viewer/README.md) for the replay contract, aggregation and visual encodings.

## Simulate and test

Use Python 3.11+, NumPy 2 and pytest 8. In the provisioned checkout use the existing environment. On a fresh checkout create it first with `python -m venv .venv`.

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENBLAS_NUM_THREADS=1
python -m pytest -q
python -m tools.eval --policy heuristic --seeds 11 12 13 --cap 100 --out results/dev.json
python -m tools.record --policy random --seed 73 --cap 100 --out replays/random-73.json
```

Evaluation writes per-game and aggregate JSON plus a companion Markdown summary. `--cohort development|refinement|held-out` labels the supplied distinct seeds. Use identical final seeds for every policy. Keep development/refinement and final validation seeds disjoint. Send only aggregate summaries for authorized refinement. Default cap is 1,000. Zero-denominator clear shares are reported as zero. Mean stack height averages the tallest occupied cell's height after each committed piece.

For a future legitimate artifact:

```bash
python -m tools.record --policy neural --weights weights/v1.npz --version "Astra v1" --seed 73 --out replays/v1-73.json
python -m tools.eval --policy neural --weights weights/v1.npz --version "Astra v1" --seeds 11 12 13 --out results/v1-dev.json
cp replays/v1-73.json viewer/data/
```

Add `{"name":"Astra v1","path":"v1-73.json"}` to the `replays` array in `viewer/data/manifest.json` and reload. Use the same seed and cap for a v2 comparison. Add the before/after hashes and percent from the diff report to the manifest's comparisons array.

## Implementation

- `tetris/` implements normalized clockwise rotations, seeded PCG64 seven-bags, vertical hard drops and simultaneous clears. `author_brief/BRIEF.md` documents spawn masks. Candidates sort by rotation then x. The lowest index wins a tie.
- `net/` validates all six finite float32 tensors and performs 205 → 128 → 32 → 1 inference on the complete candidate batch. Inputs are the post-clear binary board and a five-way one-hot clear count.
- `policies/` contains neural inference, seeded uniform random placement and a conventional linear heuristic. Heuristic coefficients for total height, lines, holes and adjacent-column bumpiness are −0.510066, +0.760666, −0.35663 and −0.184483. The random baseline records its sampled preference as a one-hot vector.
- `tools/` contains evaluation, recording, fixture generation, isolated workspace preparation and artifact inspection. `tests/` covers deterministic mechanics, inference, validation, reports, and replay consistency.
- Viewer score awards 100/300/500/800 times the pre-clear level for singles/doubles/triples/Tetrises. Level starts at one and rises every ten lines. These are display metrics. No future piece enters a policy decision.

## Experiment isolation and inspection

Use a fresh Astra session that can access **only the prepared directory**. Mounting the entire Builder repository exposes baselines, results and replay data. The isolation command copies an explicit allowlist into a new directory outside the checkout. Review the human-readable v1 dump before preparing an Editor workspace.

```bash
python -m tools.isolate author /tmp/tetris-author
python -m tools.check_rules author/build_v1.py
python -m tools.dump_weights weights/v1.npz --labels weights/v1_labels.json --out weights/dumps/v1.txt
python -m tools.isolate editor /tmp/tetris-editor
python -m tools.diff_weights weights/v1.npz weights/v2.npz --out results/v1-v2-diff.json
```

The AST checker flags common prohibited imports and calls. Manual review of source and provenance remains necessary. The diff ranks neurons by summed absolute changes in incoming weights plus bias. [PLAN.md](PLAN.md), [RULES.md](RULES.md) and [the Author brief](author_brief/BRIEF.md) specify the protocol.

## Builder freeze

The static preview is served from the separate gh-pages branch. This branch contains the application source. Use **Import replay** to open a local schema 1 recording; it is validated in the browser and becomes available in both recording selectors for the current session.

The evaluation and recording commands enforce inclusive seed ranges: development 0–9,999, refinement 10,000–10,059 and held-out 20,000–20,099. Use the entire held-out set for final comparisons. Piece order uses the original PCG64 stream; random policy decisions use child stream 1 from the same seed. New random replays identify the generator in their policy metadata.

Aggregate mean_game_mean_stack_height averages each game's mean post-placement peak height with equal weight per game. max_observed_stack_height is the tallest stack across all games. cap_reached_percent uses games as its denominator. mean_game_column_9_empty_fraction gives each game equal weight.

Prepared Author and Editor workspaces each include their own ASSIGNMENT.md. Start a fresh Astra session with access only to that directory and ask it to complete the assignment. Transfer the verified v1 artifact and labels into the Builder weights directory before creating the human-readable dump and preparing the Editor workspace.

Run Python tests with `python -m pytest -q`. Run replay validation tests with `node --test tests/replay.test.mjs`. With the local viewer served on port 8000, the provisioned Chromium and Playwright can run `node tests/viewer-smoke.cjs http://localhost:8000` for playback, comparison and real file import.

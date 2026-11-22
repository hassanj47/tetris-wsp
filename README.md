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

## Deployment and bootstrap history

The original ZIP remains in history and in the checkout. All 22 scaffold members were verified byte for byte before implementation. The intended Pages workflow is the original `.github/workflows/pages.yml` in that ZIP. It uploads only `viewer/` and requests `contents: read`, `pages: write` and `id-token: write`.

Before merging to main, an authorized maintainer must delete `.github/workflows/restore-tetris-bootstrap.yml` and restore the archive's `.github/workflows/pages.yml`. The temporary restore job triggers on main and attempts to extract the old scaffold. Updating workflow files through the GitHub App requires repository **Workflows: write** permission in addition to **Contents: write**. Enable **Settings → Pages → Source → GitHub Actions** on an eligible repository, then merge the reviewed changes and verify the deployment URL from the Pages job. Public deployment is pending.

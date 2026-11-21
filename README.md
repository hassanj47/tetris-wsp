# Tetris WSP

A reproducible demonstration of **weight-space programming (WSP)** using a Tetris-playing neural placement policy.

The experiment has two stages:

1. **Direct synthesis:** GPT-6.2 Astra writes a fixed neural network's weights directly, without conventional training.
2. **Direct weight editing:** a fresh Astra session edits the existing weights in response to a natural-language strategy instruction.

The application has two synchronized visual panels:

- **Tetris gameplay** — the actual game and selected placements.
- **Neural network** — a polished, animated view of the actual architecture, activations, and decision process.

The initial implementation is replay-first: Python executes the network and records deterministic replays in Codex Cloud; a static browser viewer renders those recordings. GitHub Pages hosts the viewer.

## Builder handoff

The static replay studio includes two explicitly labeled synthetic visualization fixtures and one recorded heuristic baseline. The fixtures exercise the fixed 205 → 128 → 32 → 1 scorer. The Astra Author and Editor experiments are pending.

### Run in Codex Cloud

From the repository root, with Python 3.11+:

```bash
python -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENBLAS_NUM_THREADS=1
python -m pytest -q
python -m http.server 8000 --directory viewer
```

Open http://localhost:8000 and press Play. Choose Compare to align two same-seed recordings. For replay fields, contribution selection, controls and publication, see [the viewer guide](viewer/README.md).

### Evaluate and record

```bash
python -m tools.eval --policy heuristic --seeds 3 4 5 --cap 100 --out results/smoke.json
python -m tools.record --policy random --seed 3 --cap 100 --out replays/random.json
```

Evaluation writes per-game and aggregate JSON plus Markdown. The default cap is 1,000. Stack height is the height of the highest occupied cell after clearing. Mean height is averaged over placements. An empty denominator yields zero for clear shares. The conventional baseline score combines aggregate column height (−0.510066), completed lines (+0.760666), holes (−0.35663), and adjacent-column bumpiness (−0.184483). The display awards 100/300/500/800 points per single/double/triple/Tetris times the pre-clear level. Level starts at one and increments every ten cumulative lines. Display score is independent of policy selection.

After the actual WSP artifacts exist:

```bash
python -m tools.record --policy neural --version v1 --weights weights/v1.npz --seed 3 --out replays/v1.json
python -m tools.eval --policy neural --version v1 --weights weights/v1.npz --seeds 3 4 5 --out results/v1-smoke.json
python -m tools.dump_weights weights/v1.npz --labels weights/v1_labels.json --out weights/dumps/v1.txt
python -m tools.diff_weights weights/v1.npz weights/v2.npz --out results/changes.json
python -m tools.check_rules author/build_v1.py
```

Use **Open replay** to load the recording in the browser. For comparison, record v2 with the same seed and cap and open both files plus the diff. For final validation use the same withheld 100 seeds across policies. The examples above use development seeds. Static script checks flag obvious forbidden imports and calls. Manual review of the construction method, session history and provenance is required.

### Separate experiment workspaces

Run the following from the Builder checkout. Give each fresh Astra session access only to its prepared directory. The Editor command requires a reviewed v1 dump and labels.

```bash
python -m tools.isolate author /tmp/tetris-author
python -m tools.isolate editor /tmp/tetris-editor
```

The tool copies an allowlist and refuses existing destinations. Place scripts and logs under author/ and weights and provenance under weights/ in the isolated directory. Provide the Editor instruction from PLAN.md. Use separate sessions with filesystem access scoped to these inputs. The Builder includes no experimental weights.

## Repository map

- `PLAN.md` — full experiment and implementation plan.
- `AGENTS.md` — instructions for the Codex Builder.
- `CODEX_BUILDER_TASK.md` — task prompt to give Codex.
- `RULES.md` — restrictions for WSP Author and Editor sessions.
- `author_brief/BRIEF.md` — isolated, self-contained network task specification.
- `tetris/` — deterministic game engine and move generation.
- `net/` — fixed MLP specification and NumPy inference.
- `policies/` — neural, random, and heuristic policies.
- `tools/` — evaluation, replay, weight inspection, and integrity checks.
- `viewer/` — static two-panel browser visualization.
- `weights/` — generated neural weight artifacts (not included yet).
- `replays/` — full simulation recordings.
- `results/` — evaluation reports.

## Experimental integrity

- Initial v1 and v2 weight authoring must be performed in separate, fresh Astra sessions.
- The Author must not see the heuristic implementation or baseline results.
- The Editor receives only the permitted v1 artifacts and the task brief.
- No training, gradient descent, optimizer, evolutionary search, or weight-search loop is permitted.
- Any optional feedback-assisted refinement must be logged and must not be described as zero-shot.
- Final validation uses a held-out, identical seed set for v1 and v2.
- The viewer must visualize actual recorded inference data, not decorative or fabricated neural activity.

## Deployment and recovery

The original ZIP remains in history and in this branch. All 22 original files were verified byte-for-byte before implementing the Builder. The task branch includes the two subsequent main-branch bootstrap commits.

Before merging to main, retire `.github/workflows/restore-tetris-bootstrap.yml` and install the original `.github/workflows/pages.yml` from the ZIP. The recovery workflow attempts to extract the scaffold on pushes to main. These workflow changes require the GitHub App repository **Workflows: write** permission in addition to **Contents: write**. The Pages job itself requests **contents: read**, **pages: write** and **id-token: write**. Set Settings → Pages → Build and deployment → Source to **GitHub Actions**. The supplied workflow publishes viewer/ on matching pushes to main and supports manual dispatch. Verify the successful deployment URL before announcing publication.

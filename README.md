# Tetris WSP

A reproducible demonstration of **weight-space programming (WSP)** using a Tetris-playing neural placement policy.

The experiment has two stages:

1. **Direct synthesis:** GPT-6.2 Astra writes a fixed neural network's weights directly, without conventional training.
2. **Direct weight editing:** a fresh Astra session edits the existing weights in response to a natural-language strategy instruction.

The application has two synchronized visual panels:

- **Tetris gameplay** — the actual game and selected placements.
- **Neural network** — a polished, animated view of the actual architecture, activations, and decision process.

The initial implementation is replay-first: Python executes the network and records deterministic replays in Codex Cloud; a static browser viewer renders those recordings. GitHub Pages hosts the viewer.

## Project status

**Bootstrap / Builder phase.** The engine, evaluation tools, replay format, and viewer are to be implemented first. The v1 and v2 weight-authoring experiments must be run later in fresh, isolated Astra sessions.

Do not claim that a Tetris WSP controller has already been generated or evaluated. No weights or performance results are included in this bootstrap.

## Quick start (after Builder implementation)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

The Builder must document the exact commands for generating replays and serving the viewer locally. Local execution is optional; the intended development and simulation environment is Codex Cloud.

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

## Deployment

The static viewer is deployed from `viewer/` using GitHub Pages and `.github/workflows/pages.yml`. The published website must work without a running Python process, Codex session, backend, or runtime API.

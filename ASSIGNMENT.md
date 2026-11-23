# Astra v3 — Feedback-Guided Weight-Space Strategy Discovery

Mission: construct a Tetris placement-scoring neural controller from zero-initialized weights, then independently discover and refine its strategy through at most three practice feedback rounds.

## Isolation
This branch is your only workspace. Do not inspect other branches, prior commits, v1/v2, prior replays, baselines, heuristic coefficients or expert gameplay examples.

## Phase 1: Initial construction
Read GAME_SPEC.md, RULES.md and DISCOVERY_PROTOCOL.md. Start all six tensors as exact zero float32 arrays. Independently devise a strategy from the rules; do not copy a supplied heuristic (none is supplied). Directly construct weights using deterministic NumPy. Keep architecture 205→128→32→1, exact tensor names/shapes/dtypes and finite values. Create author/build_v3.py, weights/v3_initial.npz, weights/v3_initial_labels.json, author/v3_initial_provenance.json and append author/LOG.md. Verify 30,529 parameters, shapes, dtype, finiteness and byte-identical rebuild. Do not execute games before this artifact is validated and committed.

## Phase 2: Practice and direct edits
Run exactly the supplied three rounds, once each:
python -m tools.practice round --number 1 --weights weights/v3_initial.npz --version "Astra v3 initial" --out-dir feedback/round-1
python -m tools.practice round --number 2 --weights weights/v3_r1.npz --version "Astra v3 revision 1" --out-dir feedback/round-2
python -m tools.practice round --number 3 --weights weights/v3_r2.npz --version "Astra v3 revision 2" --out-dir feedback/round-3

After round 1, optionally directly edit the existing arrays once: author/edit_v3_r1.py, weights/v3_r1.npz, weights/v3_r1_labels.json, author/v3_r1_provenance.json and author/v3_r1_changes.json.
After round 2, optionally create revision 2 with analogous _r2 files.
After round 3, optionally create final revision with author/edit_v3_final.py, weights/v3_final.npz, labels, provenance and change report.
Each revision must load the exact previous archive, directly edit arrays, pin input hash, preserve architecture, prove deterministic rebuild, and explain observations→hypothesis→edit. A round may be skipped if no edit is justified. Never exceed 3 rounds/3 edits.

## Phase 3: Freeze and showcase
Freeze final artifact as weights/v3_final.npz without altering contents. Rebuild entire script chain and verify reproducibility/hashes. Generate seed-73 showcase:
python -m tools.practice showcase --weights weights/v3_final.npz --version "Astra v3 final" --out viewer/data/astra-v3-seed-73.json
Validate via viewer/replay.mjs. Commit artifacts and reports to this branch. Do not run held-out evaluation or inspect baselines. Report all limitations honestly.
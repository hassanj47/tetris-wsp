# Seed-matched evaluation protocol

## Purpose

Estimate how the frozen Tetris controllers compare when random piece order is controlled. This is a separate, post-discovery evaluation. It does not modify or feed back into any controller.

## Controllers

Evaluate all six immutable archives in `evaluation/policies.json`:

1. Astra v1
2. Astra v2
3. Astra v3 initial
4. Astra v3 revision 1
5. Astra v3 revision 2
6. Astra v3 final

The v1/v2 archives must be copied from their frozen source branches exactly as specified below. Do not rebuild or edit any weights.

## Matched cohort

Use exactly the 50 seed values committed in `evaluation/COHORT.json`. They were generated deterministically from a fixed NumPy RNG seed and are disjoint from the documented development, practice and prior comparison cohorts. Do not add, remove, replace or cherry-pick seeds after seeing results.

Every controller plays every seed once: 6 × 50 = 300 games. Each seed initializes the same NumPy PCG64 seven-bag piece stream for every controller. The controllers may survive for different lengths, but the shared prefix of pieces is identical.

## Fixed environment

- 20 × 10 board
- Seven-bag I/O/T/S/Z/J/L pieces
- 205 input features and 205 → 128 → 32 → 1 network
- Candidate post-placement/post-clear boards, vertical hard drop, line clear
- No hold, next-piece preview, spins, tucks, wall kicks or post-descent horizontal movement
- Candidate ordering and tie-breaking unchanged
- Maximum 1,000 placements per game
- Official score: 0/100/300/500/800 for 0–4 lines, multiplied by current level; level rises every 10 lines

Use the frozen v3 branch runtime. The game engine, piece geometry, seven-bag generator, network inference and practice simulation source blobs are pinned in `tools/paired_eval.py`. Abort before gameplay if any pinned source hash differs.

## Outcomes and analysis

Primary outcome: official game score.

Secondary outcomes: lines, pieces survived, cap rate, clear counts, Tetrises per game, Tetris share of cleared lines, mean stack height, maximum stack height and fraction of placements with column 9 empty.

Report per-controller means and medians. For predeclared paired contrasts, report mean within-seed difference, median within-seed difference, 95% paired bootstrap confidence interval for the mean difference, and score win/tie/loss counts.

Predeclared contrasts:
- v3 final vs v3 initial (primary: overall effect of the three feedback-guided edits)
- v3 final vs v1
- v3 final vs v2
- v3 revision 1 vs v3 initial
- v3 revision 2 vs v3 revision 1
- v3 final vs v3 revision 2

Use 20,000 bootstrap resamples with a fixed analysis RNG seed. Do not select metrics or contrasts after viewing results. Treat secondary comparisons as descriptive; do not overclaim statistical significance.

## Provenance and run discipline

- Verify every archive and label SHA-256 against `evaluation/policies.json` before any game.
- Validate all six archives through `net.spec.load` (names, shapes, float32 dtypes, finite values).
- Verify all pinned source Git blob hashes before any game.
- Run unit tests and the harness's verify-only mode before gameplay.
- Commit the evaluator, cohort, policy manifest and imported v1/v2 files to `eval/seed-matched` before running.
- Run the 300-game evaluation exactly once. Do not expose interim or final results to any strategy-writing session. Do not edit weights, rerun selected seeds, tune, optimize or change the cohort.
- Keep all work in Codex Cloud. Do not touch `main`, `wsp/author-v1`, `wsp/editor-v2`, `wsp/discovery-v3`, or `eval/v1-v2-first-pass`.
- Commit the results and report only to `eval/seed-matched`.

## Interpretation

This is a paired evaluation on one fixed cohort, not proof of universal performance. A positive mean difference with an interval excluding zero is evidence of better average score on this cohort. It does not establish why a controller performs better. Because the controllers were manually authored and revised using other practice seeds, this cohort is a held-out evaluation set relative to the discovery process, not an untouched preregistered experiment in the strictest prospective sense: the cohort is fixed after the controllers were frozen. State that limitation.

# Codex Cloud run instructions — seed-matched evaluation

Work only on branch `eval/seed-matched`. Do not modify any other branch.

## Step A — import frozen v1/v2 archives

The v3 snapshots and evaluator are already present. Copy these four files byte-for-byte from the named remote branches into this branch:

- `wsp/author-v1:weights/v1.npz` → `evaluation/weights/v1.npz`
- `wsp/author-v1:weights/v1_labels.json` → `evaluation/weights/v1_labels.json`
- `wsp/editor-v2:weights/v2.npz` → `evaluation/weights/v2.npz`
- `wsp/editor-v2:weights/v2_labels.json` → `evaluation/weights/v2_labels.json`

Use Git objects / `git show` or equivalent cloud-side byte-preserving copying. Do not decode, regenerate, re-save, or otherwise alter NPZ files. Verify SHA-256 against `evaluation/policies.json`. Commit the four imported files to this branch before any game execution.

## Step B — static validation only

1. Read `EVALUATION_PROTOCOL.md`, `evaluation/COHORT.json`, `evaluation/policies.json`, and `tools/paired_eval.py`.
2. Inspect the exact pinned runtime files and confirm their git blob hashes.
3. Run the existing test suite and `python -m tools.paired_eval --verify-only`.
4. Resolve any test or static validation failure before gameplay. Do not run any game during this step.
5. Commit any harness fixes separately to this branch. Do not change the protocol, cohort, policies, expected hashes, source runtime or weights to make checks pass. If a pinned hash mismatch or source defect is found, stop and report it for review.

## Step C — execute exactly once

Only after Step B passes, execute:

```bash
python -m tools.paired_eval --run
```

This runs 300 games: six frozen controllers × 50 identical seeds. It writes a run status before starting and refuses to overwrite an existing result directory. If execution is interrupted or fails, do not rerun the cohort automatically; inspect the run status and report what happened.

Do not inspect results until the full batch completes. Do not change any weights, select seeds, tune policies, add games, or run the batch again.

## Step D — validate and publish

After successful completion:
- Validate the result JSON has 300 outcomes, every one of the 50 seeds for each of six policies.
- Confirm all six policies have identical piece-sequence hashes for each seed.
- Recompute aggregate and paired statistics independently from `per-seed.csv` / JSON and compare them with the report.
- Validate the paired bootstrap intervals and win/tie/loss counts.
- Record the exact commit, Python/NumPy versions, archive hashes, runtime hashes, cohort ID and run status.
- Commit results to `eval/seed-matched` only.

Do not modify `main`, `wsp/author-v1`, `wsp/editor-v2`, `wsp/discovery-v3`, or `eval/v1-v2-first-pass`. Do not merge anything. All work must remain in Codex Cloud; the operator will not run local commands.

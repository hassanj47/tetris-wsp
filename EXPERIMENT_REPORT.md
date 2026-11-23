# Astra v3 feedback-guided weight-space strategy discovery

The highest observed practice mean was 939,030 points for revision 1. All 20 games in its batch reached the 1,000-piece cap. Reserving the right edge more aggressively in revision 2 coincided with more four-line clears and shorter survival. The final revision softened the edge preference after the third batch. Its only game was the preassigned seed-73 showcase.

| Fixed practice batch | Controller | Mean score | Median score | Mean pieces | Mean lines | Games capped | Tetrises/game |
|---|---|---:|---:|---:|---:|---:|---:|
| 9000–9019 | Initial | 128,635 | 68,550 | 343.0 | 120.85 | 0/20 | 0.30 |
| 9020–9039 | Revision 1 | 939,030 | 946,900 | 1,000.0 | 396.85 | 20/20 | 2.40 |
| 9040–9059 | Revision 2 | 241,905 | 125,250 | 438.2 | 158.90 | 1/20 | 5.10 |

## Construction and decisions

The initial builder starts the six float32 tensors at exactly zero. It assigns weights for occupied-over-empty transitions near the floor, neighboring column load differences, height-dependent occupancy cost and line-clear payouts. The initial archive passed shape, dtype, finiteness, parameter count and byte-rebuild checks before commit d6f4d6b and before any gameplay.

1. The first three diagnostics ended with 38, 33 and 19 buried empty cells. Revision 1 changed 1,868 of 30,529 parameters. Its ReLUs count visible sky in two-row slices, giving exact buried volume and column heights across the board. The second batch had much longer survival.
2. In round 2, 5,587 of 6,633 clear events were singles. Revision 2 changed seven parameters to favor an empty right column and larger clears. The four-line share of cleared lines rose from 2.42% to 12.84% in the next batch. Mean stack height rose from 4.68 to 10.19.
3. The shortest round-3 replay spent 91.5% of placements with a single-column depression at least four cells deep. The median-role game ended with a ten-cell drop at the right edge. The final edit changed 27 parameters to reduce the edge occupancy penalty, charge for edge depth beyond three, and moderate the clear rewards. Commit f78adf6 froze the resulting archive before showcase generation.

Each batch used different seeds, so the observed score differences combine strategy and sample effects. The final artifact has no 20-game score estimate. There was no fitting, training, optimization, search, baseline inspection or held-out evaluation.

## Showcase and publication

Seed 73 scored **361,700** over **658 placements and 246 lines** (171 singles, 30 doubles, 5 triples, 0 Tetrises). It ended before the cap. The replay includes board transitions, candidate scores, placements and neural traces. The branch supplies the existing replay validator and a new uniquely named data file for additive publication. It contains no deployable Pages viewer entry point. No existing demo was replaced. Live playback on GitHub Pages has not been verified.

[Showcase replay](viewer/data/astra-v3-seed-73.json) · [Final weights](weights/v3_final.npz) · [Neuron labels](weights/v3_final_labels.json) · [Final provenance](author/v3_final_provenance.json) · [Observations and edit log](author/LOG.md) · [Artifact checksums](SHA256SUMS)

## Verification

Run `python -m author.validate_v3` at repository root to rebuild the four archives in a fresh temporary directory, check provenance and validate all ten replays. Run `sha256sum -c SHA256SUMS` to check delivery file hashes. Neither command plays games. The three practice reports include the complete aggregates and diagnostic selections.

[Round 1](feedback/round-1/REPORT.md) · [Round 2](feedback/round-2/REPORT.md) · [Round 3](feedback/round-3/REPORT.md)

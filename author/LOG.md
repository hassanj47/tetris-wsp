# Astra v3 experiment log

Initial construction and feedback rounds have not yet begun.

## Initial construction, before gameplay

The authorized ref advanced to 238e5461d9a752c0cee0336f12f870b84a541c5c. Parsed the corrected harness and exercised only its diagnostic selection statements on invented summary dictionaries. The distinct-role and repeated-role cases both selected three unique seeds. No games had run.

Hypothesis: under vertical drop, roofing an empty cell makes its column harder to repair. Count each occupied-over-empty transition in the bottom eleven rows with a binary ReLU and charge 14 score units. A compact board makes column cell counts a cheap proxy for landing heights. Charge one unit per adjacent count difference and a quarter unit for each cell's altitude, with three additional altitude units per row above altitude seven. Reward one to four cleared rows by 2, 6, 10, 16. The priorities are hand-chosen: one roof should outweigh several small surface improvements. The roof detector misses transitions above row 9 and column load underestimates height over cavities. No seed, prior policy, score, or trajectory informed these choices. Exact connections and initial zero assertion are in build_v3.py.

initial: validated and rebuilt byte-for-byte. Archive and rebuild SHA-256 bfe47746692c6f602da68e580dd4b92bdb62b4ea833a008b8552ae51f6e2feaf. See v3_initial_provenance.json for inputs and tensor counts.

## Round 1 and revision 1

Ran the prescribed initial batch once. Mean score 128635, median 68550, mean 343 pieces, 120.85 lines, no caps. Across the batch 1687 singles, 296 doubles, 38 triples, 6 Tetrises. Shortest (9006), median-role (9018), and highest (9005) replays passed the supplied validator. At termination the boards contained 38, 33, and 19 empty cells below the column tops, including 15, 15, and 8 roof transitions outside the initial detector. Their mean buried cell counts were 12.40, 3.02, 1.49. Depth-four-or-greater single-column pits occurred on 29.9%, 7.4%, 3.7% of placements. The high-score trajectory stayed relatively compact for much longer.

Hypothesis: counting buried volume and using true surface heights will distinguish deep buried gaps from shallow ones and continue operating during a high stack. Repurpose the 100 roof units to count sky cells in row pairs. Starting from two, subtract two for every cell above or in the upper row, and one for a cell in the lower row; ReLU leaves exactly zero, one or two visible sky cells. Compute buried volume as 200 minus sky minus occupied area. Set its coefficient to -10, since one tall gap now incurs multiple charges. Rewire the neighbor-difference channels to the exact column skyline. Preserve the altitude and payout terms. Exact index edits are in edit_v3_r1.py. Expected outcome: fewer large buried pockets and longer survival. New seeds limit causal inference.

r1: validated and rebuilt byte-for-byte. Archive and rebuild SHA-256 8dd72dbfc9be03948582fa76f79c01a31c8898f63125fbe43db3730cea0e70ef. See v3_r1_provenance.json for inputs and tensor counts.

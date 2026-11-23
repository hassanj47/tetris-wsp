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

## Round 2 and revision 2

Round 2 ran once with revision 1. Mean score 939030, median 946900, mean 396.85 lines, all 20 games capped. There were 5587 singles, 836 doubles, 162 triples and 48 Tetrises; four-line clears contributed 2.42% of cleared lines. Column 9 was completely empty on 20.44% of placements. All three diagnostic games lasted 1000 pieces. For shortest-role (9023), median-role (9037), and highest (9024), mean buried volumes were 1.82, 1.22, and 0.76; terminal values were 12, 0, and 0. The first had 302 singles and one Tetris versus 259 singles and two Tetrises in the highest-score replay. The latter never exceeded stack height 9. All three replay files validated.

Hypothesis: the compact boards can support a dedicated open edge and convert more rows together, for a higher score per cleared line. Remove the surface charge when column 8 exceeds column 9, charge 12 per occupied cell remaining in column 9, and use clear payouts 0, 0, 4, 12, 40. Twelve exceeds the cost of one buried cell but still allows closing the edge in exchange for a larger repair. Forty makes a four-line conversion attractive even with a moderate surface cost. This could increase stack risk while waiting for a compatible piece. Preserve all buried-volume connections. See edit_v3_r2.py for every edit.

r2: validated and rebuilt byte-for-byte. Archive and rebuild SHA-256 9356129a51335e306a29f058b99d40633dd66dd82cc29a19d512b9737396a127. See v3_r2_provenance.json for inputs and tensor counts.

## Round 3 and final revision

Round 3 ran once with revision 2. Mean score 241905, median 125250, 438.2 pieces, 158.9 lines, one cap. Four-line clears increased to 5.1/game and 12.84% of lines, while mean stack height rose to 10.19. The mean fraction with an entirely empty right column remained about 20.4%. The shortest (9052), median-role (9057), and highest (9045) replays passed validation. A one-column depression of at least four cells appeared on 91.5%, 41.2%, and 32.4% of placements respectively (boundary treated as a wall). The shortest ended with 51 buried cells. The median-role game's final right column had height 10 beside height 20. The highest scored 997400, completed 1000 pieces and cleared ten Tetrises, but averaged 5.36 buried cells. The observed survival cost outweighed the extra multiplet payouts across this batch. Different seeds prevent isolating the edit's effect.

Final hypothesis: keeping a shallow edge can retain scoring opportunities if larger edge drops become expensive. Reduce the right-column cell cost from twelve to one, restore half the normal slope charge, and add a second-layer ReLU charging two per unit of depth beyond three. This permits shallow right-edge variation without leaving a deep shaft free. Restore the initial single/double clear values and temper the four-line reward to 24. See edit_v3_final.py. Freeze this one edit, with no practice budget left to test it. The showcase cannot establish its mean score.

final: validated and rebuilt byte-for-byte. Archive and rebuild SHA-256 62fa8adae4efeecb1d28e7f12bdbbcc14de18b5d4610da0bb28403d6673ca2fb. See v3_final_provenance.json for inputs and tensor counts.

# Astra v3 experiment log

Initial construction and feedback rounds have not yet begun.

## Initial construction, before gameplay

The authorized ref advanced to 238e5461d9a752c0cee0336f12f870b84a541c5c. Parsed the corrected harness and exercised only its diagnostic selection statements on invented summary dictionaries. The distinct-role and repeated-role cases both selected three unique seeds. No games had run.

Hypothesis: under vertical drop, roofing an empty cell makes its column harder to repair. Count each occupied-over-empty transition in the bottom eleven rows with a binary ReLU and charge 14 score units. A compact board makes column cell counts a cheap proxy for landing heights. Charge one unit per adjacent count difference and a quarter unit for each cell's altitude, with three additional altitude units per row above altitude seven. Reward one to four cleared rows by 2, 6, 10, 16. The priorities are hand-chosen: one roof should outweigh several small surface improvements. The roof detector misses transitions above row 9 and column load underestimates height over cavities. No seed, prior policy, score, or trajectory informed these choices. Exact connections and initial zero assertion are in build_v3.py.

initial: validated and rebuilt byte-for-byte. Archive and rebuild SHA-256 bfe47746692c6f602da68e580dd4b92bdb62b4ea833a008b8552ae51f6e2feaf. See v3_initial_provenance.json for inputs and tensor counts.

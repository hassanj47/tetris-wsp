# Initial Astra Author v1

The Codex session constructed a single set of weights from the placement brief. The build starts all 30,529 entries at zero and assigns coefficients directly from board coordinates and the line-clear encoding. There is no random component.

## Construction

Each column gets ten first-layer units, one for each pair of consecutive rows. A unit starts at two. An occupied cell at or above the upper row subtracts two, and an occupied lower row subtracts one. After rectification, the unit counts exactly how many rows of the pair lie above the column's highest block. Summing the ten units gives the column's headroom, including twenty for an empty column. Subtracting total headroom and occupied area from 200 gives the number of empty cells below column tops. With vertical hard drops, those cells are inaccessible from above until their covering blocks clear.

The intended score adds the immediate clear reward (0, 1, 2.5, 4, or 7 for zero through four lines), then subtracts the following penalties on the resulting board.

| Quantity | Penalty per unit | Design hypothesis |
|---|---:|---|
| Covered empty cells | 5 | Avoid sealing cavities that may persist through subsequent placements. |
| Sum of column heights | 0.25 | Favor compact stacks and reward the space recovered by clears. |
| Sum of absolute height differences between neighbors | 0.5 | Favor surfaces with more accessible landing sites. |
| Sum of column heights in excess of 12, counting only positive excess | 1.5 | Increase pressure to keep tall columns away from the spawn area. |

Two directed rectifiers per boundary implement each absolute difference. The clear reward increases faster for larger clears, while the height and roughness terms can penalize maintaining a deep well. All ten columns use the same height penalties. First-layer units 102 through 127 and second-layer unit 31 are unused. The labels describe intended arithmetic roles. The strategic effects are untested hypotheses.

## Static verification

The original archive and labels were retained. A second invocation wrote into a fresh temporary directory inside the clone. Both files matched the originals byte for byte. A separate NumPy readback checked the six keys, exact shapes, float32 dtypes, finite values, total count, and the raw bytes of each tensor against the rebuild.

Gameplay sessions, policy executions, and performance evaluations all totaled zero. No training, gradients, optimization, candidate-weight search, baseline information, or evaluation feedback entered the construction. The provenance file records the prompt, inputs, versions, reproduction command and artifact digests.

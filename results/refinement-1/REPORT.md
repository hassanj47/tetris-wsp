# Astra v1 and v2 · first refinement batch

V2 kept column 9 empty more often and cleared more Tetrises. It also built higher stacks, cleared fewer lines on average and reached 1,000 pieces in 13 of 20 games. V1 reached the cap in 19. These results describe this batch.

Both policies played the same 20 refinement seeds (10000–10019) with the frozen vertical-drop engine, PCG64 seven-bag and a 1,000-piece cap. The separate seed 73 development recordings are excluded.

| Aggregate metric | Astra v1 | Astra v2 |
|---|---:|---:|
| Mean lines | 389.2 | 317.95 |
| Median lines | 397 | 392 |
| Mean pieces survived | 981.25 | 818.3 |
| Tetrises per game | 3.15 | 15.5 |
| Tetris share of clear events | 0.989% | 7.862% |
| Tetris share of cleared lines | 3.237% | 19.500% |
| Column 9 empty | 26.621% | 44.322% |
| Mean stack height | 4.6896 | 7.715 |
| Maximum observed stack height | 20 | 20 |
| Games reaching cap | 95% | 65% |

Clear shares pool events or lines across games. Column 9 counts post-placement boards with the entire column empty. Column 9 and mean height first average within each game, then give all games equal weight. Height measures the tallest occupied cell above the floor.

## Seed-matched differences

Each entry subtracts v1 from v2 on the same seed before taking the mean or median. Shares use each game’s own denominator, with zero for an empty denominator. Percentage changes below are percentage points (pp).

| Per-game metric | Mean difference | Median difference |
|---|---:|---:|
| Lines | -71.250 | -6.000 |
| Pieces survived | -162.950 | +0.000 |
| Tetrises | +12.350 | +13.000 |
| Tetris event share | +9.260 pp | +7.712 pp |
| Tetris line share | +19.210 pp | +17.726 pp |
| Column 9 empty | +17.701 pp | +17.300 pp |
| Mean stack height | +3.025 | +2.708 |
| Maximum stack height | +4.350 | +4.500 |
| Reached cap | -30.000 pp | +0.000 pp |

| V2 outcome by seed | Wins | Ties | Losses |
|---|---:|---:|---:|
| Lines | 3 | 0 | 17 |
| Pieces | 0 | 13 | 7 |

Survival differences are capped at 1,000 pieces. Games that both reach the cap tie on this measure.

## Artifact provenance

Engine and tools used builder/placement-lab at `aad0c2bb946579e0e8bd5ec351cddc5482c3aeb6`. Both archives passed the network loader’s shape, dtype and finiteness checks. The measured weight diff covers 27 of 30,529 parameters.

- Astra v1 came from `wsp/author-v1` at `073ac33743c13891d66d0788801116e4289e0226`, path `weights/v1.npz`, SHA-256 `d32aee66abee6fae581d28ecb79351fdbd6de611d3c97693161ef291e95a0114`.
- Astra v2 came from `wsp/editor-v2` at `9cc290e1b64a828f175f23689e6bbb438a5864dc`, path `weights/v2.npz`, SHA-256 `c11aa7cb3373cc8934e60637677e71dafccb060926881bbd66285eba244fd5a8`.

# Seed-matched Tetris controller evaluation

**50 shared seeds × 6 frozen controllers = 300 games.**

Source commit: `bac1e880ebda16726dd9a3bcc0873be00a1d8afc`

## Controller aggregates

| Controller | Mean score | Median score | Mean lines | Mean pieces | Cap rate | Tetrises/game |
|---|---:|---:|---:|---:|---:|---:|
| Astra v1 | 935518.0 | 949600.0 | 392.88 | 991.5 | 94.0% | 2.58 |
| Astra v2 | 542106.0 | 467550.0 | 233.62 | 617.8 | 26.0% | 13.02 |
| Astra v3 initial | 168498.0 | 70700.0 | 130.76 | 366.0 | 4.0% | 0.92 |
| Astra v3 revision 1 | 902760.0 | 936900.0 | 383.10 | 966.9 | 96.0% | 2.20 |
| Astra v3 revision 2 | 277690.0 | 127750.0 | 165.54 | 454.2 | 10.0% | 6.22 |
| Astra v3 final | 826546.0 | 939200.0 | 359.28 | 917.0 | 80.0% | 2.14 |

## Predeclared paired contrasts

Positive differences favor the left-hand controller. Confidence intervals are paired bootstrap percentile intervals (20,000 resamples).

| Contrast | Mean score difference | 95% CI | Score W/T/L | Mean lines difference | Mean pieces difference |
|---|---:|---:|---:|---:|---:|
| PRIMARY: final v3 vs initial v3 | 658048.0 | [552549.8, 752638.1] | 46/0/4 | 228.52 | 551.0 |
| final v3 vs v1 | -108972.0 | [-177916.3, -48369.4] | 20/0/30 | -33.60 | -74.5 |
| final v3 vs v2 | 284440.0 | [148077.2, 416103.0] | 33/0/17 | 125.66 | 299.2 |
| v3 revision 1 vs initial | 734262.0 | [649877.8, 810360.3] | 47/0/3 | 252.34 | 600.9 |
| v3 revision 2 vs revision 1 | -625070.0 | [-723016.2, -521510.5] | 8/0/42 | -217.56 | -512.7 |
| v3 final vs revision 2 | 548856.0 | [438546.5, 654896.8] | 43/0/7 | 193.74 | 462.8 |

## Interpretation and limitations

Controllers were frozen before this cohort was evaluated. The cohort is held out from the documented strategy-development runs, but was selected after the policies were frozen rather than preregistered before authoring. Results estimate performance on this fixed cohort and do not prove universal superiority or explain causation.

All controllers received the same 50 seeded seven-bag piece sequences (identical full 1,000-piece sequence per seed; games may terminate earlier). This is a paired simulation benchmark, not a real-world experiment. Secondary contrasts are descriptive; no multiple-comparison correction is applied.

Raw per-seed results are in `per-seed.csv` and `paired-evaluation.json`.

## Secondary outcomes by controller

Each cell gives the mean / median across the 50 games. Clear counts are events per game. The cap indicator is expressed as a percentage.

| Controller | Singles | Doubles | Triples | Tetrises |
|---|---:|---:|---:|---:|
| Astra v1 | 271.54 / 273.00 | 42.82 / 42.00 | 8.46 / 9.00 | 2.58 / 2.00 |
| Astra v2 | 81.00 / 75.00 | 24.92 / 27.00 | 16.90 / 16.00 | 13.02 / 14.00 |
| Astra v3 initial | 89.92 / 68.50 | 14.32 / 11.00 | 2.84 / 2.00 | 0.92 / 0.00 |
| Astra v3 revision 1 | 273.30 / 282.00 | 38.62 / 40.50 | 7.92 / 7.50 | 2.20 / 2.00 |
| Astra v3 revision 2 | 66.62 / 63.50 | 21.00 / 17.50 | 10.68 / 9.00 | 6.22 / 4.00 |
| Astra v3 final | 240.04 / 259.00 | 42.38 / 45.00 | 8.64 / 8.00 | 2.14 / 2.00 |

| Controller | Lines | Pieces | Capped (%) | Mean stack height | Max stack height | Column 9 empty (%) |
|---|---:|---:|---:|---:|---:|---:|
| Astra v1 | 392.88 / 398.00 | 991.46 / 1000.00 | 94.00 / 100.00 | 4.58 / 4.41 | 13.18 / 12.00 | 26.27 / 25.95 |
| Astra v2 | 233.62 / 248.00 | 617.82 / 662.50 | 26.00 / 0.00 | 8.17 / 8.06 | 19.22 / 20.00 | 47.00 / 45.93 |
| Astra v3 initial | 130.76 / 106.50 | 366.02 / 305.50 | 4.00 / 0.00 | 6.72 / 6.38 | 19.58 / 20.00 | 16.91 / 17.55 |
| Astra v3 revision 1 | 383.10 / 397.00 | 966.92 / 1000.00 | 96.00 / 100.00 | 4.84 / 4.27 | 12.36 / 11.00 | 19.11 / 20.30 |
| Astra v3 revision 2 | 165.54 / 138.00 | 454.22 / 388.00 | 10.00 / 0.00 | 10.13 / 10.02 | 19.74 / 20.00 | 17.59 / 13.92 |
| Astra v3 final | 359.28 / 395.00 | 917.00 / 1000.00 | 80.00 / 100.00 | 6.28 / 5.72 | 15.26 / 15.50 | 20.25 / 20.65 |

The pooled Tetris line share is four times the Tetris count divided by total lines. The per-game share includes games with at least one cleared line.

| Controller | Pooled Tetris line share | Mean / median per-game share | Games with cleared lines |
|---|---:|---:|---:|
| Astra v1 | 2.63% | 2.63% / 2.02% | 50 |
| Astra v2 | 22.29% | 24.90% / 23.16% | 50 |
| Astra v3 initial | 2.81% | 2.57% / 0.00% | 50 |
| Astra v3 revision 1 | 2.30% | 2.22% / 2.02% | 50 |
| Astra v3 revision 2 | 15.03% | 15.13% / 12.94% | 50 |
| Astra v3 final | 2.38% | 2.31% / 2.02% | 50 |

## Paired estimates for all three metrics

Differences are left minus right within seed. Each interval uses 20,000 paired percentile bootstrap resamples, with the analysis RNG initialized once at seed 20261125.

| Contrast | Metric | Mean difference | Median difference | 95% CI for mean |
|---|---|---:|---:|---:|
| PRIMARY: final v3 vs initial v3 | score | 658048.00 | 853150.00 | [552549.80, 752638.05] |
| PRIMARY: final v3 vs initial v3 | lines | 228.52 | 265.00 | [191.72, 262.80] |
| PRIMARY: final v3 vs initial v3 | pieces | 550.98 | 634.50 | [460.46, 634.46] |
| final v3 vs v1 | score | -108972.00 | -19600.00 | [-177916.30, -48369.40] |
| final v3 vs v1 | lines | -33.60 | -2.50 | [-54.12, -15.46] |
| final v3 vs v1 | pieces | -74.46 | 0.00 | [-122.54, -32.50] |
| final v3 vs v2 | score | 284440.00 | 264100.00 | [148077.20, 416103.00] |
| final v3 vs v2 | lines | 125.66 | 96.00 | [86.46, 165.30] |
| final v3 vs v2 | pieces | 299.18 | 230.00 | [201.90, 397.48] |
| v3 revision 1 vs initial | score | 734262.00 | 848950.00 | [649877.85, 810360.35] |
| v3 revision 1 vs initial | lines | 252.34 | 281.50 | [220.16, 281.82] |
| v3 revision 1 vs initial | pieces | 600.90 | 672.50 | [523.10, 674.70] |
| v3 revision 2 vs revision 1 | score | -625070.00 | -801950.00 | [-723016.20, -521510.50] |
| v3 revision 2 vs revision 1 | lines | -217.56 | -244.00 | [-250.64, -183.18] |
| v3 revision 2 vs revision 1 | pieces | -512.70 | -571.00 | [-594.34, -427.52] |
| v3 final vs revision 2 | score | 548856.00 | 680350.00 | [438546.45, 654896.80] |
| v3 final vs revision 2 | lines | 193.74 | 224.50 | [158.64, 228.00] |
| v3 final vs revision 2 | pieces | 462.78 | 546.00 | [378.24, 547.26] |

## Run record and independent validation

Codex Cloud ran cohort `paired-seed-cohort-2026-11-24` once with Python 3.12.14 and NumPy 2.5.5. The run status is `complete` at 300 of 300 games. Before execution, all 12 tests and the evaluator’s verify-only checks passed.

Independent analysis matched every CSV field to its JSON outcome, regenerated the 50 PCG64 stream hashes, and checked the six policy records on each seed. Checks covered clear-count identities, cap flags, metric bounds, all controller aggregates, within-seed means and medians, all six score win/tie/loss counts, and all 18 bootstrap intervals. The two evaluator-generated report tables agreed at their displayed precision. The stream hashes identify the full seeded input stream. Each policy consumed a prefix through termination or the cap.

| Controller | Archive SHA-256 | Label SHA-256 |
|---|---|---|
| Astra v1 | `d32aee66abee6fae581d28ecb79351fdbd6de611d3c97693161ef291e95a0114` | `eff4307bef7e69bd389427da299c0f17554dac9b6bb94f40177e67f8bb819f54` |
| Astra v2 | `c11aa7cb3373cc8934e60637677e71dafccb060926881bbd66285eba244fd5a8` | `dc52a8bec65d2fa50ed774b261f6a4820db751549fcde78532133cfe5bdfdac8` |
| Astra v3 initial | `bfe47746692c6f602da68e580dd4b92bdb62b4ea833a008b8552ae51f6e2feaf` | `8669b031c90a4ec24f225a369c7fd3c0ef00dfe5536d9b2d906156537f5dc2b8` |
| Astra v3 revision 1 | `8dd72dbfc9be03948582fa76f79c01a31c8898f63125fbe43db3730cea0e70ef` | `75b1ceee60282448c602a9f2b821d36c2fca239270f974380d9f227cd8f7e32f` |
| Astra v3 revision 2 | `9356129a51335e306a29f058b99d40633dd66dd82cc29a19d512b9737396a127` | `54c24ce187ab3e01f236fcbfc70ceb2766f4c2f38eb81a92f1795b547e92da78` |
| Astra v3 final | `62fa8adae4efeecb1d28e7f12bdbbcc14de18b5d4610da0bb28403d6673ca2fb` | `31dc20d026ac1216866d9cad0685116dc4cd1caae8807e6c4479a5d0f4777b61` |

| Pinned source | Git blob SHA-1 |
|---|---|
| `tetris/engine.py` | `e517ee90b95e03657ee406b43baeb373dbdecfdd` |
| `tetris/moves.py` | `e9579bc21d73e079a9ed1c16f1258c0ad027327a` |
| `tetris/rng.py` | `f112d4f2bc3d3955ca0b132b112575d232b6bfe9` |
| `tetris/pieces.py` | `3708b4425c18c53abc4544987c508454b4ce036c` |
| `net/mlp.py` | `48a62bb3d3abe802e3045fcdef4a9e254fffbab7` |
| `net/spec.py` | `a6185fc29bda196748009af1f7183c5449a326db` |
| `tools/practice.py` | `2b8929a4da54698b4d40b632bb55354d68c4e282` |

| Raw data | SHA-256 |
|---|---|
| `per-seed.csv` | `b1323e547c5a67a438bb5fd4a2d17f4401936ff29d6ef44403710651fca71637` |
| `paired-evaluation.json` | `2c040ac7208f7c1f3bdff9c2ca41d5e06ef71fb2b986f87b49540cd2c551b35f` |

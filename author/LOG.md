# Astra Editor v2 · initial attempt

The supplied v1 archive matched SHA-256 `d32aee66abee6fae581d28ecb79351fdbd6de611d3c97693161ef291e95a0114`. I inspected the unit labels, the reviewed dump, and the arrays. The dump shows zero incoming weights at h1[102] and h2[31], a unit-weight clear-reward relay from h1[101] to h2[30], and an output weight of −0.5 on h2[18].

I copied the six v1 arrays and assigned 27 entries by index. On a binary post-clear board let n be the number of occupied cells in column 9. The hypothesized role of repurposed h1[102] is an empty-well indicator, with preactivation 1 − n. The hypothesized role of repurposed h2[31] is its thresholded relay, with preactivation 2 × h1[102] − 1. With output weight 8 and offset −8, this path contributes zero for an empty well and −8 for any obstruction. The fixed penalty values the first obstruction even if it is only one cell and allows other score terms to outweigh it.

I removed the output cost on h2[18], the labeled positive height difference from column 8 to column 9. This lets a four-row lip grow beside the well without paying the old 0.5 per row of height difference. I raised the four-line input weight at W1[204,101] from 7 to 24. The existing smaller-clear rewards are 1, 2.5, and 4. The additional 17 points favor taking an available Tetris while keeping board quality relevant. These are design intentions. Actual well maintenance and clear frequencies are unmeasured.

| Tensor | Changed / total | Changed (%) | Absolute delta × count |
| --- | ---: | ---: | --- |
| W1 | 21 / 26,240 | 0.080030 | 1 × 20, 17 × 1 |
| b1 | 1 / 128 | 0.781250 | 1 × 1 |
| W2 | 1 / 4,096 | 0.024414 | 2 × 1 |
| b2 | 1 / 32 | 3.125000 | 1 × 1 |
| W3 | 2 / 32 | 6.250000 | 0.5 × 1, 8 × 1 |
| b3 | 1 / 1 | 100.000000 | 8 × 1 |
| Overall | 27 / 30,529 | 0.088440 | 0.5 × 1, 1 × 22, 2 × 1, 8 × 2, 17 × 1 |

I reloaded the saved archive and checked names, shapes, float32 dtypes, finite values, exact change counts and magnitude distributions against v1. A second invocation into a fresh temporary directory reproduced the weights, labels and change report byte for byte. Reproduce from the repository root with `python author/edit_v2.py`. Use `--output-root DIR` for an independent comparison. The experiment ended at static validation with zero policy executions, games, or evaluations. No training, optimization, weight search, baseline inspection or evaluation feedback informed the edits.

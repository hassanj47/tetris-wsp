# Replay studio

Serve this directory with any static HTTP server. Assets and recordings resolve relative to the page, including under a GitHub Pages project subpath. All replay data is loaded from the same static origin.

The Recording selector drives the network. Compare with adds a second board on the same placement clock. Comparison requires the same seed, rules, bag, board size and cap. When one run ends its final board and metrics freeze. Use the primary selector to inspect the other network. Seeking and single-stepping show the committed board. The opening fixture is paused at placement eight; drag the timeline to the first placement for the full run.

The Network view groups the 200 board inputs by row (mean occupancy) and shows five separate clear-count inputs. Each hidden dot represents one unit. Brightness is scaled within each layer for the selected move. Pulses follow the top 24 nonzero absolute activation-times-weight contributions per transition. Their color indicates sign. Weight inspection lists exact source and destination indices, weight, and contribution. Features lists candidate scores and the selected post-clear board. Baselines have no activation trace. Upcoming pieces are read from subsequent recorded frames only.

## Static data contract, version 1

Manifest entries are objects with `name` and relative `path` inside `data/`. Optional `comparisons` entries take `before`, `after` (weight file SHA-256 hashes) and `percent` directly from the diff report. Only matching pairs show a changed percentage.

Each replay contains `schema_version`, `seed`, `config`, `policy`, `game`, `shapes` and ordered `frames`. Shapes hold normalized [dx,dy] coordinates by piece and rotation. Policy provenance includes implementation version, display version and, for neural policies, artifact filename and SHA-256. Each frame contains:

- 20×10 `before` and `after` boards with 0 for empty and 1–7 for I,O,T,S,Z,J,L.
- Current `piece`, ordered `candidates` encoded as [rotation,x,landing_y,score], and zero-based `selected`.
- Pre-clear row indices in `cleared` and post-placement cumulative `stats`.
- Neural `trace.layers` with the full selected input, first hidden and second hidden vectors. The output is the selected score. Each `trace.edges` entry contains [source index,target index,weight,source activation × weight]. Bias is included in inference and excluded from edges. A baseline's trace is null.

The two included synthetic QA fixtures share one seeded set of random tensors except for a sign flip in the output weights. They demonstrate comparison and inference visualization. Rebuild with `OPENBLAS_NUM_THREADS=1 python -m tools.viewer_fixtures` from the repository root. Only their replays and a measured change percentage are retained.

# Replay studio

Serve this directory from any static HTTP server. From the repository root, run `python -m http.server 8000 --directory viewer` and open http://localhost:8000. Python is just one way to preview static files. The deployed application uses relative same-origin assets and has no backend or runtime dependencies.

Choose a recording, press Play, or use the placement slider and step buttons. The selected score and network correspond to the candidate whose landing outline appears on the board. Features lists every legal placement in engine order. Weights shows the six recorded tensor summaries. Baselines expose candidate rankings and carry no neural signals.

Compare aligns the two boards by piece number. Only recordings with identical seed, cap and rules qualify. A shorter run holds its final board while the longer one finishes. The recording selector determines the primary network. Open replay accepts local replay files and weight-diff JSON, including multiple files at once. Change percentage requires a diff matching the artifact hashes or two identical hashes.

## Replay schema 1

The top level contains schema_version, seed, config (cap and rules), policy (kind, version, artifact, SHA-256), piece_ids, frames and final metrics. Neural replays include tensor shape, extrema and nonzero counts. The bundled synthetic recordings have fixture=true. The fixture generation script uses deterministic numerical test inputs solely to exercise this UI.

Each frame stores 20×10 before/after piece-ID arrays, piece name, selected candidate index, absolute landing cells, cleared row indices before removal, ordered candidates (rotation, x, y, score), and post-placement cumulative stats. Indexing starts at zero. Random scores are seeded IID priorities. The current piece is the only piece available to the player.

For the chosen neural candidate, neural contains full x, h1 and h2 vectors. Its scalar output is the selected candidate's score. Each adjacent layer pair records up to 16 largest nonzero connections by absolute source activation × weight, with source index, destination index, signed weight and contribution. Positive contributions appear green and negative contributions coral. Biases are included in inference. Brightness of a unit is normalized within its layer. Motion illustrates one recorded forward pass. The display clock controls interpolation and does not affect game state.

To publish additional recordings, copy their JSON to data/, then append an entry with name, path (relative to viewer/), seed, cap and rules to data/manifest.json. To publish a comparison, include the complete output of tools.diff_weights in the manifest's diffs array. The SHA-256 fields link the comparison to the exact replay artifacts.

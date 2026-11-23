# Imported frozen controller archives

The v1 and v2 archives and labels must be copied byte-for-byte from the frozen source branches:
- `wsp/author-v1:weights/v1.npz`
- `wsp/author-v1:weights/v1_labels.json`
- `wsp/editor-v2:weights/v2.npz`
- `wsp/editor-v2:weights/v2_labels.json`

Expected SHA-256 values are pinned in `../policies.json`. Do not rebuild or modify them. The v3 snapshots are already present in the repository's `weights/` directory.

"""Rebuild Astra v2 from the reviewed v1 archive using only static array edits."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
V1_SHA256 = "d32aee66abee6fae581d28ecb79351fdbd6de611d3c97693161ef291e95a0114"
SHAPES = {"W1": (205, 128), "b1": (128,), "W2": (128, 32),
          "b2": (32,), "W3": (32, 1), "b3": (1,)}


def validate(tensors):
    if set(tensors) != set(SHAPES):
        raise ValueError("Unexpected tensor names")
    for name, shape in SHAPES.items():
        a = tensors[name]
        if a.shape != shape or a.dtype != np.float32 or not np.isfinite(a).all():
            raise ValueError(f"Invalid tensor {name}")


def summarize(delta):
    magnitudes = np.abs(delta[delta != 0])
    values, counts = np.unique(magnitudes, return_counts=True)
    return {"parameters": delta.size, "changed": magnitudes.size,
            "percent_changed": 100 * magnitudes.size / delta.size,
            "absolute_delta_histogram": [
                {"magnitude": float(v), "count": int(n)} for v, n in zip(values, counts)
            ]}


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(destination):
    archive = ROOT / "weights/v1.npz"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != V1_SHA256:
        raise ValueError("Supplied v1 SHA-256 mismatch")
    with np.load(archive, allow_pickle=False) as loaded:
        original = {name: loaded[name] for name in loaded.files}
    validate(original)
    v2 = {name: original[name].copy() for name in SHAPES}

    # First ReLU yields one exactly when column 9 is empty on a binary board.
    v2["W1"][9:200:10, 102] = -1
    v2["b1"][102] = 1
    # A threshold at 1/2 passes that binary flag, with unit output when active.
    v2["W2"][102, 31] = 2
    v2["b2"][31] = -1
    # Anchor the empty-well term at zero, with a fixed cost for any obstruction.
    v2["W3"][31, 0] = 8
    v2["b3"][0] = -8
    # Remove the inherited slope cost just for column 8 rising above column 9.
    v2["W3"][18, 0] = 0
    # Increase the existing four-line reward from 7 to 24.
    v2["W1"][204, 101] = 24
    validate(v2)

    labels = json.loads((ROOT / "weights/v1_labels.json").read_text())
    labels["h1"][101] = "Immediate clear reward for counts 0 through 4: 0, 1, 2.5, 4, 24"
    labels["h1"][102] = "Hypothesis: indicator of an empty column 9 on a post-clear board"
    labels["h2"][18] += " (disconnected from placement score)"
    labels["h2"][31] = "Hypothesis: relay of empty-column-9 indicator to the score"

    delta = {k: v2[k].astype(np.float64) - original[k] for k in SHAPES}
    report = {"definition": "Exact v2 minus v1. Percentages use all parameters in scope. "
                            "Histograms count only nonzero absolute deltas.",
              "overall": summarize(np.concatenate([d.ravel() for d in delta.values()])),
              "by_tensor": {k: summarize(d) for k, d in delta.items()}}
    for directory in ["author", "weights"]:
        (destination / directory).mkdir(parents=True, exist_ok=True)
    np.savez(destination / "weights/v2.npz", **v2)
    write_json(destination / "weights/v2_labels.json", labels)
    write_json(destination / "author/v2_changes.json", report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    build(parser.parse_args().output_root)

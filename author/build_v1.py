"""Construct the initial placement-scoring tensors without executing the network."""
import argparse
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SHAPES = {
    "W1": (205, 128), "b1": (128,), "W2": (128, 32),
    "b2": (32,), "W3": (32, 1), "b3": (1,),
}


def validate(tensors):
    if set(tensors) != set(SHAPES):
        raise ValueError("Unexpected tensor names")
    for name, shape in SHAPES.items():
        value = tensors[name]
        if value.shape != shape or value.dtype != np.float32 or not np.isfinite(value).all():
            raise ValueError(f"Invalid tensor {name}")
    if sum(value.size for value in tensors.values()) != 30529:
        raise ValueError("Unexpected parameter count")


def construct():
    tensors = {key: np.zeros(shape, dtype=np.float32) for key, shape in SHAPES.items()}
    w1, b1, w2, b2, w3 = (tensors[key] for key in ("W1", "b1", "W2", "b2", "W3"))
    first = ["Unused"] * 128
    second = ["Unused"] * 32

    for column in range(10):
        units = slice(10 * column, 10 * column + 10)
        for pair in range(10):
            unit = units.start + pair
            upper_row = 2 * pair
            lower_row = upper_row + 1
            # Any block at or above the upper row exhausts both free slots.
            w1[column:10 * lower_row:10, unit] = -2
            w1[10 * lower_row + column, unit] = -1
            b1[unit] = 2
            first[unit] = f"Headroom in rows {upper_row} and {lower_row} of column {column}"

        w2[units, 0:2] = -1
        w2[units, 20 + column] = -1
        b2[20 + column] = 8
        w3[20 + column, 0] = -1.5
        second[20 + column] = f"Height above 12 in column {column}"

    w1[:200, 100] = 1
    first[100] = "Occupied cell count"
    w2[100, 0] = -1
    b2[:2] = 200
    second[:2] = ["Covered empty cell count", "Sum of column heights"]
    w3[:2, 0] = [-5, -0.25]

    for column in range(9):
        left = slice(10 * column, 10 * column + 10)
        right = slice(left.stop, left.stop + 10)
        unit = 2 + 2 * column
        w2[left, unit:unit + 2] = [-1, 1]
        w2[right, unit:unit + 2] = [1, -1]
        w3[unit:unit + 2, 0] = -0.5
        for offset, (a, b) in enumerate(((column, column + 1), (column + 1, column))):
            second[unit + offset] = f"Positive part of height in column {a} minus height in {b}"

    w1[200:205, 101] = [0, 1, 2.5, 4, 7]
    first[101] = "Immediate line-clear reward from the five one-hot inputs"
    w2[101, 30] = 1
    w3[30, 0] = 1
    second[30] = "Pass through line-clear reward"
    labels = {
        "description": "Intended unit roles on valid inputs. Strategic effects are hypotheses.",
        "indexing": "Zero-based unit, row and column indices. Row 0 is the top.",
        "h1": first, "h2": second, "output": ["Placement score, higher is preferred"],
    }
    return tensors, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "weights")
    directory = parser.parse_args().output_dir
    tensors, labels = construct()
    validate(tensors)
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory / "v1.npz"
    np.savez(archive, **tensors)
    with np.load(archive, allow_pickle=False) as saved:
        validate(saved)
    (directory / "v1_labels.json").write_bytes((json.dumps(labels, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()

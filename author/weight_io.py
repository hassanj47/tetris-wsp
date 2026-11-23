"""Shared archive and validation operations. Run builders as Python modules."""
import argparse
from pathlib import Path

import numpy as np

from net.spec import SHAPES, digest, load


def destination(default):
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path(default))
    return parser.parse_args().out


def save(path, weights):
    np.savez(path, **weights)
    recovered = load(path)
    assert sum(t.size for t in recovered.values()) == 30529
    for name, original in weights.items():
        np.testing.assert_array_equal(recovered[name], original)


def pinned(path, expected):
    if digest(path) != expected:
        raise ValueError(f'Unexpected parent archive: {path}')
    return load(path)

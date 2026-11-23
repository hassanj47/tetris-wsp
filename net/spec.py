import hashlib
from pathlib import Path
import numpy as np

SHAPES = dict(W1=(205, 128), b1=(128,), W2=(128, 32), b2=(32,), W3=(32, 1), b3=(1,))


def load(path):
    with np.load(path, allow_pickle=False) as data:
        if sorted(data.files) != sorted(SHAPES):
            raise ValueError("unexpected tensor names")
        weights = dict(data)
    for name, shape in SHAPES.items():
        tensor = weights[name]
        if tensor.shape != shape or tensor.dtype != np.float32 or not np.isfinite(tensor).all():
            raise ValueError(f"invalid tensor {name}, expected finite float32 {shape}")
    return weights


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

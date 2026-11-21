from hashlib import sha256
from pathlib import Path
import numpy as np

SHAPES = {"W1":(205,128), "b1":(128,), "W2":(128,32), "b2":(32,), "W3":(32,1), "b3":(1,)}

def load(path):
    with np.load(path, allow_pickle=False) as data:
        if sorted(data.files) != sorted(SHAPES):
            raise ValueError("expected exactly six named tensors")
        weights = dict(data)
    for name, shape in SHAPES.items():
        a = weights[name]
        if a.shape != shape or a.dtype != np.float32 or not np.isfinite(a).all():
            raise ValueError(f"invalid shape, dtype or value in {name}")
    return weights

def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()

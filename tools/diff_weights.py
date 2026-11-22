import argparse
import numpy as np
from net.spec import load, digest
from .simulation import write_json
from pathlib import Path


def compare(a, b):
    tensors = {}
    largest = []
    for name in a:
        delta = np.abs(a[name].astype(float) - b[name])
        changed = int(np.count_nonzero(delta))
        tensors[name] = dict(changed=changed, total=delta.size, percent=100*changed/delta.size,
                             mean_absolute=float(delta.mean()), max_absolute=float(delta.max()))
    for i in range(1,4):
        key = f"W{i}"
        movement = np.abs(a[key].astype(float)-b[key]).sum(axis=0)
        movement += np.abs(a[f"b{i}"].astype(float)-b[f"b{i}"])
        largest.extend((float(v), i, j) for j,v in enumerate(movement) if v)
    count = sum(t["changed"] for t in tensors.values())
    total = sum(t["total"] for t in tensors.values())
    return dict(changed=count, total=total, percent=100*count/total, tensors=tensors,
                largest_neurons=sorted(largest,reverse=True)[:20])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.out, dict(before=digest(args.before), after=digest(args.after),
                              **compare(load(args.before),load(args.after))))

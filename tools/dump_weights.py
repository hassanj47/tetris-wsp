import argparse
import json
import numpy as np
from pathlib import Path
from net.spec import load, digest


def dump(weights):
    lines = ["30,529 float32 parameters. Indices are zero-based."]
    for key, a in weights.items():
        lines.append(f"{key} {a.shape}: range [{a.min():g}, {a.max():g}], nonzero {np.count_nonzero(a)}")
        if key.startswith("b"):
            lines.append(str(a.tolist()))
            continue
        for j, col in enumerate(a.T):
            top = np.argsort(-np.abs(col), kind="stable")[:8]
            entries = ", ".join(f"{i}={col[i]:.6g}" for i in top if col[i])
            lines.append(f"{key}[:,{j}] strongest incoming: {entries or 'all zero'}")
            if key == "W1":
                lines.extend(" ".join(f"{v:.4g}" for v in row) for row in col[:200].reshape(20,10))
                lines.append(f"clear-count inputs: {col[200:].tolist()}")
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("weights")
    p.add_argument("--labels",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args = p.parse_args()
    report = digest(args.weights)+"\n"+dump(load(args.weights))
    if args.labels:
        report += "\nAuthor-supplied hypotheses:\n"+json.dumps(json.loads(args.labels.read_text()),indent=2)
    args.out.write_text(report+"\n")

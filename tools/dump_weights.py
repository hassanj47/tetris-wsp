import argparse
import json
from pathlib import Path
import numpy as np
from net.spec import load,digest

def dump(path,labels=None):
    w=load(path)
    lines=[f"SHA-256 {digest(path)}",f"Parameters {sum(a.size for a in w.values())}"]
    if labels:
        lines.extend(["Author labels (hypotheses)",json.dumps(json.loads(labels.read_text()),indent=2)])
    for name,a in w.items():
        lines.append(f"{name} {a.shape} | range {a.min():g} to {a.max():g} | nonzero {np.count_nonzero(a)}")
        if name.startswith("b"):
            lines.append(" ".join(map(str,a)))
        else:
            for i,col in enumerate(a.T):
                indices=np.argsort(-np.abs(col),kind="stable")[:8]
                lines.append(f"Unit {i}, strongest inputs: "+", ".join(f"{j}={col[j]:g}" for j in indices if col[j]))
                if name=="W1":
                    lines.extend(" ".join(f"{value:.5g}" for value in row) for row in col[:200].reshape(20,10))
                    lines.append("Clear bits: "+" ".join(map(str,col[200:])))
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Produce a human-readable artifact dump")
    p.add_argument("path");p.add_argument("--labels",type=Path);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(dump(a.path,a.labels))

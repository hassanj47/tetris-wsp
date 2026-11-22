"""Generate deterministic display-only QA recordings. Never evaluate these as experiments."""
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from net.spec import SHAPES, digest
from tools.simulation import simulate, write_json
from tools.diff_weights import compare

DATA = Path(__file__).resolve().parents[1]/"viewer/data"


def main():
    rng = np.random.default_rng(319)
    a = {k: rng.normal(0, .15, shape).astype(np.float32) for k,shape in SHAPES.items()}
    b = {k:v.copy() for k,v in a.items()}
    b["W3"] *= -1
    entries = []
    with TemporaryDirectory() as scratch:
        hashes = []
        for label, w in [("Fixture A",a), ("Fixture B",b), ("Heuristic baseline",None)]:
            policy = "heuristic" if w is None else "neural"
            path = Path(scratch)/(label.replace(" ","-")+".npz")
            if w is not None:
                np.savez(path, **w)
                hashes.append(digest(path))
            args = Namespace(policy=policy, weights=path if w is not None else None, version=label, cap=48)
            replay = simulate(args, 73, True)
            replay["policy"]["fixture"] = w is not None
            filename = label.lower().replace(" ","-")+".json"
            write_json(DATA/filename,replay)
            entries.append(dict(name=label,path=filename))
        write_json(DATA/"manifest.json",dict(schema_version=1,replays=entries,
                   comparisons=[dict(before=hashes[0],after=hashes[1],percent=compare(a,b)["percent"])]))


if __name__ == "__main__":
    main()

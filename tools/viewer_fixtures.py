"""Rebuild synthetic viewer QA recordings. Never use these in evaluations."""
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from net.spec import SHAPES
from policies.placement import Policy
from .simulation import run,write
from .diff_weights import compare

def main():
    out=Path("viewer/data")
    rng=np.random.default_rng(42)
    w={k:rng.normal(0,.15,s).astype(np.float32) for k,s in SHAPES.items()}
    catalog=[]
    seed,cap=17,45
    with TemporaryDirectory() as temp:
        paths=[]
        for name in ["fixture-a","fixture-b","heuristic"]:
            if name=="heuristic":
                policy=Policy("heuristic",seed)
                label="Heuristic baseline"
            else:
                if name=="fixture-b":
                    w["W3"]=-w["W3"]
                path=Path(temp)/(name+".npz")
                np.savez(path,**w)
                paths.append(path)
                label="Synthetic fixture "+name[-1].upper()
                policy=Policy("neural",seed,path,label)
                policy.meta["artifact"]=path.name
            _,rep=run(seed,cap,policy,True)
            rep["fixture"]=name!="heuristic"
            write(out/(name+".json"),rep)
            catalog.append(dict(name=label,path="data/"+name+".json",seed=seed,cap=cap,rules=rep["config"]["rules"]))
        write(out/"manifest.json",dict(schema_version=1,replays=catalog,diffs=[compare(*paths)]))

if __name__=="__main__":
    main()

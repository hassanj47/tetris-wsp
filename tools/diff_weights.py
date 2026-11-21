import argparse
from pathlib import Path
import numpy as np
from net.spec import load,digest
from .simulation import write

def compare(a,b):
    left,right=load(a),load(b)
    tensors={}
    changed=total=0
    neurons=[]
    for name,values in left.items():
        delta=right[name].astype(float)-values
        count=int(np.count_nonzero(delta))
        changed+=count
        total+=values.size
        tensors[name]=dict(changed=count,percent=100*count/values.size,
                           max_abs=float(np.abs(delta).max()),l1=float(np.abs(delta).sum()))
        if name.startswith("W"):
            bias="b"+name[1:]
            norms=np.abs(delta).sum(axis=0)+np.abs(right[bias].astype(float)-left[bias])
            neurons.extend(dict(layer=int(name[1:]),unit=i,l1=float(v)) for i,v in enumerate(norms) if v)
    return dict(before=digest(a),after=digest(b),changed=changed,total=total,percent=100*changed/total,
                tensors=tensors,largest_neurons=sorted(neurons,key=lambda n:-n["l1"])[:16])

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Compare two fixed MLP artifacts")
    p.add_argument("before");p.add_argument("after");p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    write(a.out,compare(a.before,a.after))

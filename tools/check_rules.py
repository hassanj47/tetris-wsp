"""Static review aid. Passing does not certify protocol compliance."""
import argparse
import ast
from pathlib import Path

FORBIDDEN={"torch","tensorflow","jax","optax","keras","sklearn","scipy.optimize","tetris","policies","tools"}
OPERATIONS={"fit","backward","minimize","train","grad","apply_gradients","differential_evolution"}

def check(source):
    issues=[]
    tree=ast.parse(source)
    for node in ast.walk(tree):
        names=[]
        if isinstance(node,ast.Import):
            names=[a.name for a in node.names]
        elif isinstance(node,ast.ImportFrom):
            names=[(node.module or "")+"."+a.name for a in node.names]
        elif isinstance(node,ast.Call):
            op=getattr(node.func,"attr",getattr(node.func,"id",""))
            if op in OPERATIONS: issues.append((node.lineno,op))
        for name in names:
            if any(name==bad or name.startswith(bad+".") for bad in FORBIDDEN):
                issues.append((node.lineno,name))
    return sorted(issues)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("script",type=Path)
    a=p.parse_args()
    issues=check(a.script.read_text())
    for line,reason in issues: print(f"{a.script}:{line}: {reason}")
    raise SystemExit(bool(issues))

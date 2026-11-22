"""Advisory static review; cannot prove compliance or detect every alias."""
import argparse
import ast
from pathlib import Path

BLOCKED = {"torch","keras","tensorflow","jax","optax","scipy.optimize","sklearn","gym",
           "stable_baselines3","deap","tetris","policies","tools.eval","tools.record","tools.simulation"}
CALLS = {"backward","fit","minimize","optimize","backprop","gradient","grad","train"}


def findings(source):
    issues = []
    for node in ast.walk(ast.parse(source)):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [f"{node.module}.{a.name}" for a in node.names]
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func).split(".")[-1]
            if name in CALLS:
                issues.append(f"{node.lineno}: review call to {name}")
        for name in names:
            if any(name == p or name.startswith(p+".") for p in BLOCKED):
                issues.append(f"{node.lineno}: review import {name}")
    return issues


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("script",type=Path)
    issues = findings(p.parse_args().script.read_text())
    print("\n".join(issues) or "No flagged patterns. Manual review is still required.")
    raise SystemExit(bool(issues))

"""Advisory static review; cannot prove compliance or detect every alias."""
import argparse
import ast
from pathlib import Path

BLOCKED = {"torch","keras","tensorflow","jax","optax","scipy.optimize","sklearn","gym",
           "stable_baselines3","deap","tetris","policies","tools"}
CALLS = {"backward","fit","minimize","optimize","backprop","gradient","grad","train","apply_gradients",
         "differential_evolution","backpropagate","fit_transform"}


def findings(source):
    issues = []
    tree = ast.parse(source)
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                aliases[a.asname or a.name] = f"{node.module}.{a.name}"
        elif isinstance(node, ast.Import):
            aliases.update({a.asname: a.name for a in node.names if a.asname})
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [f"{node.module}.{a.name}" for a in node.names]
        elif isinstance(node, ast.Call):
            parts = ast.unparse(node.func).split(".")
            parts[0] = aliases.get(parts[0], parts[0])
            target = ".".join(parts)
            name = target.split(".")[-1]
            names.append(target)
            if name in {"__import__", "import_module"}:
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    names.append(node.args[0].value)
                else:
                    issues.append(f"{node.lineno}: review dynamic import")
            if name in {"eval", "exec"}:
                issues.append(f"{node.lineno}: review dynamic execution")
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

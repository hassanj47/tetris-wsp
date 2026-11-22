"""Prepare an allowlisted workspace outside the Builder checkout."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def prepare(role, dest):
    dest = dest.resolve()
    if dest == ROOT or ROOT in dest.parents:
        raise ValueError("choose a fresh directory outside this repository")
    files = ["RULES.md","author_brief/BRIEF.md"]
    if role == "editor":
        files += ["weights/v1.npz","weights/v1_labels.json","weights/dumps/v1.txt"]
    if not all((ROOT/f).is_file() for f in files):
        raise ValueError("required inputs missing; review and prepare the v1 dump first")
    dest.mkdir(parents=True, exist_ok=False)
    for name in files:
        (dest/name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dest/name)
    for folder in ["author","weights"]:
        (dest/folder).mkdir(exist_ok=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("role", choices=["author","editor"])
    p.add_argument("destination", type=Path)
    args = p.parse_args()
    prepare(args.role, args.destination)

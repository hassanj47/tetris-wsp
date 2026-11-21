"""Create a new minimal workspace outside the Builder repository."""
import argparse
from pathlib import Path
import shutil
from net.spec import load

def prepare(role,dest,root):
    dest=dest.resolve()
    if dest.is_relative_to(root.resolve()) or dest.exists():
        raise ValueError("choose a new directory outside the Builder checkout")
    paths=["RULES.md","author_brief/BRIEF.md"]
    if role=="editor":
        paths+=["weights/v1.npz","weights/v1_labels.json","weights/dumps/v1.txt"]
        load(root/"weights/v1.npz")
    for name in paths:
        if not (root/name).is_file(): raise FileNotFoundError(name)
    dest.mkdir(parents=True)
    for directory in ["author","weights","author_brief","weights/dumps"]:
        (dest/directory).mkdir(exist_ok=True)
    for name in paths: shutil.copyfile(root/name,dest/name)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("role",choices=["author","editor"]);p.add_argument("dest",type=Path)
    a=p.parse_args()
    prepare(a.role,a.dest,Path(__file__).resolve().parents[1])

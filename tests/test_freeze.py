from itertools import islice
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pytest

from net.spec import SHAPES
from policies.random_policy import random_policy
from tetris.rng import seven_bag
from tools.check_rules import findings
from tools.cohorts import COHORTS, validate_seeds
from tools.eval import aggregate
from tools import isolate


def test_policy_rng_is_independent_of_piece_stream():
    seed = 73
    choices = random_policy(seed)
    bag = seven_bag(seed)
    expected = list(islice(seven_bag(seed), 35))
    child = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(1,)))
    root = np.random.default_rng(seed)
    observed = []
    for piece in expected:
        assert next(bag) == piece
        for _ in range(3):
            observed.append(choices(range(17))[0].argmax())
    assert observed == child.integers(17, size=len(observed)).tolist()
    assert observed != root.integers(17, size=len(observed)).tolist()


@pytest.mark.parametrize("name", COHORTS)
def test_cohort_boundaries(name):
    allowed = COHORTS[name]
    validate_seeds(name, [allowed.start, allowed.stop-1])
    for other, seeds in COHORTS.items():
        if name != other:
            assert set(allowed).isdisjoint(seeds)
    for invalid in [[allowed.start-1], [allowed.stop], [allowed.start]*2]:
        with pytest.raises(ValueError):
            validate_seeds(name, invalid)


@pytest.mark.parametrize("module,option", [("eval","--seeds"),("record","--seed")])
def test_cli_rejects_wrong_cohort(tmp_path, module, option):
    path = tmp_path/"bad.json"
    p = subprocess.run([sys.executable,"-m","tools."+module,"--policy","random",
                        "--cohort","development",option,"20000","--out",str(path)],capture_output=True)
    assert p.returncode == 2 and b"development requires" in p.stderr
    assert not path.exists()


def test_stack_height_aggregates():
    game = dict(lines=0, singles=0, doubles=0, triples=0, tetrises=0, capped=False,
                pieces=2, mean_stack_height=2, max_stack_height=3, column_9_empty_fraction=1)
    summary = aggregate([game, dict(game, pieces=8, mean_stack_height=8,max_stack_height=12)])
    assert summary["mean_game_mean_stack_height"] == 5
    assert summary["max_observed_stack_height"] == 12


@pytest.mark.parametrize("code", [
    "from importlib import import_module as get\nget('tools.eval')",
    "from numpy import gradient as g\ng(x)",
    "import scipy as sp\nsp.optimize.differential_evolution(f,bounds)",
    "__import__(module_name)",
    "exec(script)",
])
def test_advisory_flags(code):
    assert findings(code)
    assert not findings("import numpy as np\nx = np.maximum(0, np.arange(5))")


def test_editor_only_receives_validated_inputs(tmp_path, monkeypatch):
    root = tmp_path/"builder"
    for name in ["RULES.md","author_brief/BRIEF.md","assignments/editor.md"]:
        (root/name).parent.mkdir(exist_ok=True,parents=True)
        shutil.copyfile(isolate.ROOT/name,root/name)
    (root/"weights/dumps").mkdir(parents=True)
    (root/"weights/dumps/v1.txt").write_text("reviewed test dump")
    (root/"weights/v1_labels.json").write_text("{}")
    weights = root/"weights/v1.npz"
    tensors = {k:np.zeros(shape,np.float32) for k,shape in SHAPES.items()}
    np.savez(weights,**dict(tensors,b3=np.array([np.inf],np.float32)))
    monkeypatch.setattr(isolate,"ROOT",root)
    dest = tmp_path/"editor"
    with pytest.raises(ValueError,match="invalid tensor"):
        isolate.prepare("editor",dest)
    assert not dest.exists()
    np.savez(weights,**tensors)
    isolate.prepare("editor",dest)
    assert weights.read_bytes() == (dest/"weights/v1.npz").read_bytes()
    assert (dest/"ASSIGNMENT.md").read_bytes() == (root/"assignments/editor.md").read_bytes()
    assert sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()) == [
        "ASSIGNMENT.md","RULES.md","author_brief/BRIEF.md","weights/dumps/v1.txt",
        "weights/v1.npz","weights/v1_labels.json"]

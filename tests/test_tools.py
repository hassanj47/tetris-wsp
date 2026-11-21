from pathlib import Path
import json
import numpy as np
import pytest
from net.spec import SHAPES
from tools.check_rules import check
from tools.dump_weights import dump
from tools.diff_weights import compare
from tools.isolate import prepare
from tools.eval import aggregate

def test_diff_and_dump(tmp_path):
    a,b=[tmp_path/n for n in ("a.npz","b.npz")]
    w={k:np.zeros(s,np.float32) for k,s in SHAPES.items()}
    np.savez(a,**w)
    w["W1"][1,2]=-2
    w["b1"][2]=3
    np.savez(b,**w)
    d=compare(a,b)
    assert d["changed"]==2 and d["total"]==30529
    assert d["largest_neurons"][0]==dict(layer=1,unit=2,l1=5)
    assert "Parameters 30529" in dump(b)
    assert "1=-2" in dump(b)

def test_rules():
    assert len(check("import torch as t\nfrom scipy import optimize\na.fit(b)"))==3
    assert not check("import numpy as np\nw=np.zeros(2)")

def test_isolate(tmp_path):
    dest=tmp_path/"isolated"
    root=Path(__file__).resolve().parents[1]
    prepare("author",dest,root)
    assert {str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()}=={"RULES.md","author_brief/BRIEF.md"}
    with pytest.raises(ValueError): prepare("author",dest,root)
    with pytest.raises(ValueError): prepare("author",root/"session",root)

def test_metrics():
    g=dict(lines=5,pieces=50,tetrises=1,singles=1,doubles=0,triples=0,cap_reached=True,column_9_empty_fraction=.4)
    s=aggregate([g])
    assert s["tetris_event_share"]==.5 and s["tetris_line_share"]==.8
    assert s["cap_reached_percent"]==100

def test_bundled_replays():
    data=Path("viewer/data")
    manifest=json.loads((data/"manifest.json").read_text())
    for e in manifest["replays"]:
        r=json.loads((data.parent/e["path"]).read_text())
        assert r["schema_version"]==1 and r["metrics"]["pieces"]==len(r["frames"])
        for f in r["frames"]:
            scores=[c["score"] for c in f["candidates"]]
            assert f["selected"]==scores.index(max(scores))
            if r["fixture"]:
                n=f["neural"]
                assert [len(n[k]) for k in ("x","h1","h2")]==[205,128,32]
                for values,edges in zip((n["x"],n["h1"],n["h2"]),n["edges"]):
                    for edge in edges:
                        assert np.isclose(edge["value"],values[edge["src"]]*edge["weight"])
            else: assert f["neural"] is None

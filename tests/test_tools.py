from argparse import Namespace
import json
import numpy as np
import pytest
from tools.simulation import simulate
from tools.eval import aggregate
from tools.diff_weights import compare
from tools.check_rules import findings
from tools.isolate import prepare
from net.spec import SHAPES


def test_replay_metrics_and_order():
    args = Namespace(policy="heuristic",version=None,weights=None,cap=100)
    r = simulate(args, 19, True)
    assert r == simulate(args, 19, True)
    assert r["game"]["lines"] > 0 and r["game"]["capped"]
    for i,f in enumerate(r["frames"]):
        if i:
            assert f["before"] == r["frames"][i-1]["after"]
        rot,x,y,score = f["candidates"][f["selected"]]
        locked = np.array(f["before"])
        for dx,dy in r["shapes"][f["piece"]][rot]:
            assert locked[y+dy,x+dx] == 0
            locked[y+dy,x+dx] = 1
        rows = np.flatnonzero(locked.all(axis=1)).tolist()
        assert rows == f["cleared"] and score == max(c[3] for c in f["candidates"])
        after = np.vstack((np.zeros((len(rows),10)), np.delete(locked,rows,axis=0)))
        assert np.array_equal(after!=0,np.array(f["after"])!=0)
    assert aggregate([r["game"]])["cap_percent"] == 100


def test_aggregate_denominators():
    game = dict(lines=6,singles=2,doubles=0,triples=0,tetrises=1,pieces=23,capped=False,
                column_9_empty_fraction=.5)
    stats = aggregate([game])
    assert stats["tetris_event_share"] == 1/3 and stats["tetris_line_share"] == 4/6


def test_diff_and_rule_guard():
    a={k:np.zeros(s,np.float32) for k,s in SHAPES.items()}
    b={k:v.copy() for k,v in a.items()}
    b["b2"][3]=5
    d=compare(a,b)
    assert d["changed"]==1 and d["total"]==30529 and d["largest_neurons"]==[(5.,2,3)]
    assert findings("from scipy import optimize\nmodel.fit(x)")
    assert findings("import numpy as np\nx=np.zeros(10)") == []


def test_isolation(tmp_path):
    dest = tmp_path/"author"
    prepare("author",dest)
    assert {str(f.relative_to(dest)) for f in dest.rglob("*") if f.is_file()} == {"RULES.md","author_brief/BRIEF.md"}
    with pytest.raises(FileExistsError): prepare("author",dest)


def test_manifest_fixture_provenance():
    from tools.viewer_fixtures import DATA
    manifest=json.loads((DATA/"manifest.json").read_text())
    for entry in manifest["replays"]:
        r=json.loads((DATA/entry["path"]).read_text())
        for f in r["frames"]:
            if not f["trace"]:
                assert r["policy"]["type"]!="neural"
                continue
            if r["policy"].get("fixture"):
                assert "Fixture" in entry["name"]
            t=f["trace"]
            assert [len(v) for v in t["layers"]]==[205,128,32]
            for layer,edges in zip(t["layers"],t["edges"]):
                assert all(layer[i]*weight==contribution for i,_,weight,contribution in edges)

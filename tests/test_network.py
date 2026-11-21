import numpy as np
import pytest
from net.spec import SHAPES,load
from net.mlp import encode,forward,trace
from policies.placement import Policy
from tetris.engine import Game
from tools.simulation import run
from tools.eval import aggregate

@pytest.fixture
def weights():
    return {k:np.zeros(s,np.float32) for k,s in SHAPES.items()}

@pytest.mark.parametrize("fault",["dtype","shape","nan","inf","extra","missing"])
def test_validation(weights,tmp_path,fault):
    if fault=="dtype": weights["b1"]=weights["b1"].astype(float)
    if fault=="shape": weights["W3"]=weights["W3"].T
    if fault=="nan": weights["W1"][0,0]=np.nan
    if fault=="inf": weights["W1"][0,0]=np.inf
    if fault=="extra": weights["extra"]=np.array(1)
    if fault=="missing": del weights["b3"]
    path=tmp_path/"bad.npz"
    np.savez(path,**weights)
    with pytest.raises(ValueError): load(path)

def test_relu_and_contributions(weights):
    moves=Game(2).moves
    x=encode(moves)
    assert x.dtype==np.float32 and x.shape==(len(moves),205)
    assert (x[:,200]==1).all()
    np.testing.assert_array_equal(x[0,:200],moves[0].board.ravel()!=0)
    weights["W1"][200,:2]=[2,-3]
    weights["W2"][0,2]=4
    weights["W3"][2,0]=-2
    weights["b3"][0]=1
    scores,layers=forward(x,weights)
    assert (scores==-15).all()
    assert layers[1][0,1]==0
    assert trace(layers,weights,0)["edges"][2]==[dict(src=2,dst=0,weight=-2,value=-16)]

def test_replay_ties(weights,tmp_path):
    path=tmp_path/"zero.npz"
    np.savez(path,**weights)
    _,rep=run(1,8,Policy("neural",1,path),True)
    for f in rep["frames"]:
        assert f["selected"]==0 and len(f["neural"]["h1"])==128
    assert rep["metrics"]["cap_reached"]
    assert rep["frames"][0]["after"]==rep["frames"][1]["before"]

@pytest.mark.parametrize("kind",["random","heuristic"])
def test_baselines(kind):
    g,r=run(3,75,Policy(kind,3),True)
    assert (g,r)==run(3,75,Policy(kind,3),True)
    assert all(f["neural"] is None for f in r["frames"])
    if kind=="heuristic": assert g["lines"]>0 and g["cap_reached"]
    assert aggregate([g])["mean_lines"]==g["lines"]

import numpy as np
import pytest
from net.spec import SHAPES, load
from net.mlp import encode, strongest
from policies.net_policy import neural
from tetris.moves import placements


def tensors():
    return {k: np.zeros(s, np.float32) for k,s in SHAPES.items()}


@pytest.mark.parametrize("issue", ["key","extra","dtype","shape","nan","inf"])
def test_bad_artifacts(tmp_path, issue):
    w = tensors()
    if issue == "key": del w["W2"]
    if issue == "extra": w["other"] = w["b1"]
    if issue == "dtype": w["W2"] = w["W2"].astype(float)
    if issue == "shape": w["W2"] = w["W2"].T
    if issue in ("nan","inf"): w["W2"][0,0] = float(issue)
    np.savez(tmp_path/"w.npz", **w)
    with pytest.raises(ValueError): load(tmp_path/"w.npz")


def test_forward_trace_and_encoding(tmp_path):
    w = tensors()
    w["W1"][200, 1] = 2
    w["b1"][0] = -8
    w["W2"][1, 7] = 3
    w["W3"][7] = -4
    w["b3"][0] = 5
    np.savez(tmp_path/"w.npz", **w)
    moves = placements(np.zeros((20,10),np.uint8), "O")
    x = encode(moves)
    assert x.dtype == np.float32 and x.shape == (9,205) and x[0].sum() == 5
    assert np.array_equal(x[0,:200], moves[0].board.ravel() != 0)
    scores, trace = neural(load(tmp_path/"w.npz"), True)(moves)
    assert np.all(scores == -19)
    assert trace["layers"][1][:2] == [0,2]
    assert trace["edges"][2] == [[7,0,-4,-24]]
    assert strongest(np.zeros(32),w["W3"]) == []

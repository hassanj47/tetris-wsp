from pathlib import Path
import argparse
import json
import numpy as np
from net.mlp import trace
from policies.placement import Policy
from tetris.engine import Game
from tetris.pieces import IDS

def run(seed, cap, policy, record=False):
    game = Game(seed,cap)
    frames, heights = [], []
    events = [0]*5
    score = empty = lines = 0
    while game.moves:
        index,scores,layers = policy.decide(game.moves)
        m = game.moves[index]
        n = len(m.rows)
        events[n] += 1
        score += [0,100,300,500,800][n]*(1+lines//10)
        lines += n
        height = 20-int(np.flatnonzero(m.board.any(axis=1))[0]) if m.board.any() else 0
        heights.append(height)
        empty += int(not m.board[:,9].any())
        if record:
            frames.append(dict(before=game.board.tolist(),after=m.board.tolist(),piece=game.piece,
                cells=m.cells,rows=m.rows,selected=index,
                candidates=[dict(rotation=c.rotation,x=c.x,y=c.y,score=float(s)) for c,s in zip(game.moves,scores)],
                neural=trace(layers,policy.weights,index) if layers is not None else None,
                stats=dict(pieces=game.pieces+1,lines=lines,tetrises=events[4],score=score,
                           level=1+lines//10,column_9_empty_fraction=empty/(game.pieces+1))))
        game.step(index)
    metrics = dict(seed=seed,lines=lines,pieces=game.pieces,singles=events[1],doubles=events[2],
        triples=events[3],tetrises=events[4],cap_reached=game.pieces==cap,
        mean_stack_height=float(np.mean(heights)),max_stack_height=max(heights),
        column_9_empty_fraction=empty/game.pieces)
    replay = dict(schema_version=1,seed=seed,config=dict(cap=cap,rules="vertical-drop-v1"),
                  policy=policy.meta,piece_ids=IDS,frames=frames,metrics=metrics)
    if record and policy.weights is not None:
        replay["tensors"] = {k:dict(shape=v.shape,min=float(v.min()),max=float(v.max()),
                                nonzero=int(np.count_nonzero(v))) for k,v in policy.weights.items()}
    return metrics,replay

def parser(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--policy", choices=["random","heuristic","neural"], required=True)
    p.add_argument("--weights",type=Path)
    p.add_argument("--version")
    p.add_argument("--cap",type=int,default=1000)
    p.add_argument("--out",type=Path,required=True)
    return p

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n")

def simulate(args,seed,record=False):
    return run(seed,args.cap,Policy(args.policy,seed,args.weights,args.version),record)

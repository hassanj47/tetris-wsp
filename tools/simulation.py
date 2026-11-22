import argparse
import json
from pathlib import Path
import numpy as np
from .cohorts import COHORTS
from net.spec import load, digest
from policies.heuristic_policy import heuristic
from policies.random_policy import random_policy
from policies.net_policy import neural
from tetris.engine import play
from tetris.pieces import SHAPES

CONFIG = dict(rules="vertical-drop-1", board=[20, 10], bag="numpy-PCG64-seven-bag")


def arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--policy", choices=["random", "heuristic", "neural"], required=True)
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--version", help="Displayed artifact name for a neural policy")
    parser.add_argument("--cap", type=int, default=1000)
    parser.add_argument("--cohort", choices=COHORTS, default="development")
    parser.add_argument("--out", required=True, type=Path)
    return parser


def policy(args, seed, recording):
    info = dict(type=args.policy, version=args.version or args.policy, implementation="builder-1")
    if args.policy == "neural":
        if not args.weights:
            raise ValueError("neural policy needs --weights")
        weights = load(args.weights)
        info.update(sha256=digest(args.weights), artifact=args.weights.name)
        return neural(weights, recording), info
    if args.policy == "random":
        info.update(implementation="builder-2", rng="PCG64-SeedSequence-child-1")
    if args.weights:
        raise ValueError("--weights requires a neural policy")
    return (heuristic if args.policy == "heuristic" else random_policy(seed)), info


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n")


def simulate(args, seed, recording=False):
    choose, info = policy(args, seed, recording)
    events = [0]*5
    score = height_sum = max_height = empty_well = lines = pieces = 0
    frames = []
    for before, piece, moves, scores, index, trace in play(seed, args.cap, choose):
        move = moves[index]
        count = len(move.rows)
        events[count] += 1
        pieces += 1
        score += (0, 100, 300, 500, 800)[count] * (1 + lines//10)
        lines += count
        filled = np.flatnonzero(move.board.any(axis=1))
        height = 20-int(filled[0]) if filled.size else 0
        max_height = max(height, max_height)
        height_sum += height
        empty_well += int(not move.board[:, 9].any())
        if recording:
            frames.append(dict(before=before.tolist(), after=move.board.tolist(), piece=piece,
                               candidates=[[m.rotation, m.x, m.y, float(s)] for m, s in zip(moves, scores)],
                               selected=index, cleared=move.rows, trace=trace,
                               stats=dict(pieces=pieces, lines=lines, level=1+lines//10, score=score,
                                          tetrises=events[4], column_9_empty_fraction=empty_well/pieces)))
    game = dict(seed=seed, lines=lines, pieces=pieces, singles=events[1], doubles=events[2],
                triples=events[3], tetrises=events[4], capped=pieces == args.cap,
                mean_stack_height=height_sum/max(1,pieces), max_stack_height=max_height,
                column_9_empty_fraction=empty_well/max(1,pieces))
    result = dict(schema_version=1, config={**CONFIG, "cap":args.cap}, seed=seed, policy=info, game=game)
    if recording:
        result.update(frames=frames, shapes=SHAPES)
    return result

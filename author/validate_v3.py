"""Verify the rebuild chain, recorded inputs, practice samples and replays without games."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from net.spec import digest, load

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text())


def run():
    os.chdir(ROOT)
    replay_paths = []
    modules = ['build_v3', 'edit_v3_r1', 'edit_v3_r2', 'edit_v3_final']
    with tempfile.TemporaryDirectory() as scratch:
        (Path(scratch) / 'weights').mkdir()
        for stage, module in zip(['initial', 'r1', 'r2', 'final'], modules):
            meta = read(f'author/v3_{stage}_provenance.json')
            for path, expected in meta['inputs_and_labels'].items():
                assert digest(path) == expected, path
            subprocess.run([sys.executable, '-m', f'author.{module}'], cwd=scratch,
                           env=dict(os.environ, PYTHONPATH=str(ROOT)), check=True)
            artifact = meta['output']
            assert digest(Path(scratch) / artifact) == digest(artifact) == meta['sha256'] == meta['rebuild_sha256']
            assert sum(a.size for a in load(artifact).values()) == 30529
    for n, stage in enumerate(['initial', 'r1', 'r2'], 1):
        folder = Path(f'feedback/round-{n}')
        feedback = read(folder / 'feedback.json')
        seeds = list(range(8980 + n * 20, 9000 + n * 20))
        assert feedback['seeds'] == seeds == [g['seed'] for g in feedback['games']]
        expected = digest(f'weights/v3_{stage}.npz')
        assert feedback['weight_sha256'] == expected
        diags = feedback['diagnostic_replays']
        assert len(diags) == len({d['seed'] for d in diags}) == 3
        for d in diags:
            path = folder / d['path']
            r = read(path)
            assert r['policy']['sha256'] == expected and r['seed'] == d['seed']
            assert r['game'] == feedback['games'][seeds.index(d['seed'])]
            replay_paths.append(path)
    showcase = Path('viewer/data/astra-v3-seed-73.json')
    r = read(showcase)
    assert r['seed'] == 73 and r['policy']['sha256'] == digest('weights/v3_final.npz')
    replay_paths.append(showcase)
    js = """import fs from 'node:fs'; import {validateReplay} from './viewer/replay.mjs';
    for(const p of process.argv.slice(1)){
      const r=validateReplay(JSON.parse(fs.readFileSync(p)));
      if(r.game.score!==r.frames.at(-1).stats.score)throw Error('final score '+p);
    }"""
    subprocess.run(['node', '--input-type=module', '-e', js, *replay_paths], check=True)
    print('Verified four byte-identical builds, three fixed batches, nine diagnostic replays and showcase.')


if __name__ == '__main__':
    run()

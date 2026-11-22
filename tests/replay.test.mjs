import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateReplay} from '../viewer/replay.mjs';

const fixture = name => JSON.parse(readFileSync(new URL('../viewer/data/'+name+'.json',import.meta.url)));
for (const name of ['fixture-a','fixture-b','heuristic-baseline']){
  test('reconstruct complete '+name,()=>validateReplay(fixture(name)));
}
const corruptions={
  architecture:r=>r.frames[0].trace.layers[1].pop(),
  contribution:r=>r.frames[0].trace.edges[1][0][3]++,
  candidate:r=>r.frames[0].candidates.pop(),
  landing:r=>r.frames[0].candidates[0][2]--,
  winner:r=>r.frames[0].selected=(r.frames[0].selected+1)%r.frames[0].candidates.length,
  score:r=>r.frames[0].candidates[0][3]=Infinity,
  board:r=>r.frames[1].before[0][0]=9,
  reconstruction:r=>r.frames[0].after[19][0]=8,
  stats:r=>r.frames[2].stats.score++,
  summary:r=>r.game.pieces++,
  encoding:r=>r.frames[0].trace.layers[0][0]=2,
  shapes:r=>r.shapes.I[0].pop(),
  provenance:r=>r.policy.sha256='missing',
};
for(const [name,corrupt] of Object.entries(corruptions)){
  test('reject invalid '+name,()=>{const r=fixture('fixture-a');corrupt(r);assert.throws(()=>validateReplay(r),/Invalid replay/);});
}

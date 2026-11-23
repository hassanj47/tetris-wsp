// Schema 1 uses normalized clockwise rotations in (x, y) screen coordinates.
const masks = {I:['IIII'], O:['OO','OO'], T:['.T.','TTT'], S:['.SS','SS.'],
  Z:['ZZ.','.ZZ'], J:['J..','JJJ'], L:['..L','LLL']};
const pieces = Object.keys(masks);
const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const sized = (a,n) => Array.isArray(a) && a.length === n;
const bounded = (v,min,max) => Number.isSafeInteger(v) && v >= min && v <= max;
const emptyRow = () => Array(10).fill(0);
const emptyBoard = () => Array.from({length:20}, emptyRow);
const canonical = {};
for (const [piece, mask] of Object.entries(masks)) {
  let cells = mask.flatMap((row,y) => [...row].flatMap((c,x) => c === '.' ? [] : [[x,y]]));
  const turns = [];
  for (let r=0; r<4; r++) {
    const left=Math.min(...cells.map(c=>c[0])), top=Math.min(...cells.map(c=>c[1]));
    cells=cells.map(([x,y])=>[x-left,y-top]).sort(([x,y],[u,v])=>x-u || y-v);
    if (!turns.some(t=>same(t,cells))) turns.push(cells);
    cells=cells.map(([x,y])=>[-y,x]);
  }
  canonical[piece]=turns;
}

function check(ok, field) {
  if (!ok) throw Error('Invalid replay: '+field);
}

function checkTrace(trace, after, cleared) {
  const widths=[205,128,32,1];
  check(sized(trace?.layers,3) && sized(trace.edges,3),'trace layers');
  const input=after.flat().map(Number).map(v=>Number(v!==0)).concat([0,1,2,3,4].map(n=>Number(n===cleared)));
  check(same(trace.layers[0],input),'encoded input');
  for (let l=0;l<3;l++) {
    const a=trace.layers[l], edges=trace.edges[l];
    check(sized(a,widths[l]) && a.every(v=>Number.isFinite(v) && v>=0),'activations');
    check(Array.isArray(edges) && edges.length<=24,'edges');
    const seen=new Set();
    let previous=Infinity;
    for (const edge of edges) {
      check(sized(edge,4),'edge');
      const [i,j,w,c]=edge;
      check(bounded(i,0,widths[l]-1) && bounded(j,0,widths[l+1]-1) && Number.isFinite(w)
        && Number.isFinite(c) && c!==0 && a[i]*w===c && Math.abs(c)<=previous && !seen.has(i+','+j),'edge contribution');
      previous=Math.abs(c); seen.add(i+','+j);
    }
  }
}

export function validateReplay(r) {
  check(r?.schema_version===1 && bounded(r.seed,0,Number.MAX_SAFE_INTEGER),'header');
  const config=r.config, policy=r.policy;
  check(config?.rules==='vertical-drop-1' && config.bag==='numpy-PCG64-seven-bag' &&
    same(config.board,[20,10]) && bounded(config.cap,1,1000),'configuration');
  check(['neural','heuristic','random'].includes(policy?.type) && typeof policy.version==='string'
    && policy.version.length && typeof policy.implementation==='string','policy');
  if (policy.type==='neural') check(typeof policy.sha256==='string' && /^[a-f0-9]{64}$/.test(policy.sha256)
    && typeof policy.artifact==='string' && policy.artifact.length,'artifact provenance');
  for (const p of pieces) check(same(r.shapes?.[p],canonical[p]),'piece shapes');
  check(Array.isArray(r.frames) && bounded(r.frames.length,1,config.cap),'frames');
  let board=emptyBoard(), score=0, lines=0, wells=0, heightSum=0, peak=0;
  const counts=[0,0,0,0,0], bag=new Set();
  for (const [n,f] of r.frames.entries()) {
    check(f && same(board,f.before) && pieces.includes(f.piece),'starting board or piece at '+n);
    if (n%7===0) bag.clear();
    check(!bag.has(f.piece),'seven-bag sequence'); bag.add(f.piece);
    check(Array.isArray(f.candidates) && bounded(f.selected,0,f.candidates.length-1),'selection');
    const ceiling=emptyRow().map((_,x)=>{const y=board.findIndex(row=>row[x]!==0);return y===-1?20:y;});
    let index=0, best=0;
    for (const [rot,cells] of canonical[f.piece].entries()) {
      const width=1+Math.max(...cells.map(c=>c[0]));
      for (let x=0;x<=10-width;x++) {
        const y=Math.min(...cells.map(([dx,dy])=>ceiling[x+dx]-dy-1));
        if (y<0) continue;
        const c=f.candidates[index];
        check(sized(c,4) && c[0]===rot && c[1]===x && c[2]===y && Number.isFinite(c[3]),'legal candidates');
        if (c[3]>f.candidates[best][3]) best=index;
        index++;
      }
    }
    check(index===f.candidates.length && best===f.selected,'candidate count or winning score');
    const [rot,x,y]=f.candidates[best];
    for (const [dx,dy] of canonical[f.piece][rot]) board[y+dy][x+dx]=pieces.indexOf(f.piece)+1;
    const rows=board.flatMap((row,i)=>row.every(Boolean)?[i]:[]);
    board=Array.from({length:rows.length},emptyRow).concat(board.filter((_,i)=>!rows.includes(i)));
    check(same(rows,f.cleared) && same(board,f.after),'reconstructed placement at '+n);
    counts[rows.length]++;
    score += [0,100,300,500,800][rows.length]*(1+Math.floor(lines/10));
    lines += rows.length;
    wells += Number(board.every(row=>row[9]===0));
    const first=board.findIndex(row=>row.some(Boolean)), height=first===-1?0:20-first;
    heightSum+=height; peak=Math.max(peak,height);
    const stats=f.stats;
    check(stats?.pieces===n+1 && stats.lines===lines && stats.level===1+Math.floor(lines/10)
      && stats.tetrises===counts[4] && stats.score===score && stats.column_9_empty_fraction===wells/(n+1),'placement metrics');
    if (policy.type==='neural') checkTrace(f.trace,board,rows.length);
    else check(f.trace===null,'baseline trace');
  }
  const n=r.frames.length, g=r.game;
  check(g?.pieces===n && g.seed===r.seed && g.lines===lines && g.capped===(n===config.cap)
    && same([g.singles,g.doubles,g.triples,g.tetrises],counts.slice(1))
    && g.mean_stack_height===heightSum/n && g.max_stack_height===peak && g.column_9_empty_fraction===wells/n,'game summary');
  return r;
}

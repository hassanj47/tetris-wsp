import { validateReplay } from "./replay.mjs";

const $ = id => document.getElementById(id);
const PIECE_IDS = " IOTSZJL";
const PIECE_COLORS = {
  I:"#65d7df", O:"#f1cb73", T:"#b7a0ff", S:"#8bd5a1",
  Z:"#ef91a8", J:"#8eafff", L:"#f1a878"
};
const state = { a:null, b:null, index:0, phase:0, playing:false, speed:2 };
const cache = new Map();
let manifest = null, raf = 0, lastTime = 0, loadToken = 0;
const TOTAL = () => Math.max(state.a?.frames.length || 0, state.b?.frames.length || 0);
const ease = t => t*t*(3-2*t);
const fmt = n => Math.round(n).toLocaleString("en-US");

async function readJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error("Could not load " + path + " (" + response.status + ")");
  return response.json();
}
async function getReplay(path) {
  if (!cache.has(path)) {
    const raw = await readJson("data/" + path);
    cache.set(path, validateReplay(raw));
  }
  return cache.get(path);
}
function sharedSequence(a,b) {
  if (a.seed !== b.seed) return false;
  if (JSON.stringify(a.config) !== JSON.stringify(b.config)) return false;
  const n = Math.min(a.frames.length,b.frames.length);
  for (let i=0;i<n;i++) if (a.frames[i].piece !== b.frames[i].piece) return false;
  return true;
}
function pause() {
  state.playing = false;
  $("play").textContent = "▶";
  $("play").setAttribute("aria-label","Play");
  cancelAnimationFrame(raf);
}
async function loadPair() {
  const token = ++loadToken;
  pause();
  $("syncStatus").textContent = "Loading recorded games and inference…";
  try {
    const [a,b] = await Promise.all([getReplay($("runA").value),getReplay($("runB").value)]);
    if (token !== loadToken) return;
    if (a.policy.type !== "neural" || b.policy.type !== "neural") throw new Error("Choose two neural-network recordings.");
    if (!sharedSequence(a,b)) throw new Error("These recordings do not share the same seed and piece sequence.");
    state.a = a; state.b = b; state.index = 0; state.phase = 0;
    $("seek").max = String(TOTAL()-1);
    $("seek").value = "0";
    $("syncStatus").textContent = "MATCHED · SEED " + a.seed + " · SAME SEVEN-BAG PIECE STREAM";
    $("titleA").textContent = a.policy.version;
    $("titleB").textContent = b.policy.version;
    $("decisionNameA").textContent = a.policy.version;
    $("decisionNameB").textContent = b.policy.version;
    render();
  } catch (error) {
    if (token === loadToken) $("syncStatus").textContent = "Replay error · " + error.message;
  }
}
function currentFrame(r) {
  return r.frames[Math.min(state.index,r.frames.length-1)];
}
function statsAt(r) {
  if (state.index >= r.frames.length) return r.frames[r.frames.length-1].stats;
  if (state.phase >= .92) return currentFrame(r).stats;
  return state.index === 0
    ? {score:0,lines:0,level:1,pieces:0,tetrises:0,column_9_empty_fraction:0}
    : r.frames[state.index-1].stats;
}
function cell(ctx,x,y,color,ghost=false,alpha=1) {
  if (y < -1 || y > 20) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  const px=x*30+2, py=y*30+2;
  if (ghost) {
    ctx.strokeStyle=color; ctx.lineWidth=1.7;
    ctx.strokeRect(px+1,py+1,24,24);
    ctx.fillStyle=color; ctx.globalAlpha=alpha*.13;
    ctx.fillRect(px+1,py+1,24,24);
  } else {
    ctx.fillStyle=color;
    ctx.fillRect(px,py,26,26);
    ctx.fillStyle="#ffffff28";
    ctx.fillRect(px+1,py+1,24,3);
    ctx.fillStyle="#00000020";
    ctx.fillRect(px+1,py+23,24,2);
  }
  ctx.restore();
}
function drawBoard(canvas,r,index,phase) {
  const ctx=canvas.getContext("2d");
  ctx.clearRect(0,0,300,600);
  const finished=index>=r.frames.length;
  const f=r.frames[Math.min(index,r.frames.length-1)];
  const settled=finished || phase>=.92;
  const board=settled ? f.after : f.before;
  ctx.fillStyle="#09121a";ctx.fillRect(0,0,300,600);
  ctx.strokeStyle="#1c2a35";ctx.lineWidth=.8;
  for(let y=0;y<=20;y++){ctx.beginPath();ctx.moveTo(0,y*30);ctx.lineTo(300,y*30);ctx.stroke();}
  for(let x=0;x<=10;x++){ctx.beginPath();ctx.moveTo(x*30,0);ctx.lineTo(x*30,600);ctx.stroke();}
  board.forEach((row,y)=>row.forEach((v,x)=>{if(v)cell(ctx,x,y,PIECE_COLORS[PIECE_IDS[v]]);}));
  if (!settled) {
    const candidate=f.candidates[f.selected];
    const rot=candidate[0], targetX=candidate[1], targetY=candidate[2];
    const shape=r.shapes[f.piece][rot];
    const color=PIECE_COLORS[f.piece];
    shape.forEach(([dx,dy])=>cell(ctx,targetX+dx,targetY+dy,color,true,.62));
    const progress=ease(Math.min(1,phase/.82));
    const startX=3;
    const x=startX+(targetX-startX)*progress;
    const y=-2+(targetY+2)*progress;
    shape.forEach(([dx,dy])=>cell(ctx,Math.round(x)+dx,Math.round(y)+dy,color,false,1));
    if (phase>.82 && f.cleared.length) {
      const flash=(phase-.82)/.10;
      ctx.fillStyle="rgba(224,255,240,"+(Math.max(0,1-flash)*.42)+")";
      f.cleared.forEach(row=>ctx.fillRect(0,row*30,300,30));
    }
  }
  if (finished) {
    ctx.fillStyle="#071018b8";ctx.fillRect(0,0,300,600);
    ctx.fillStyle="#f2f5f4";ctx.textAlign="center";ctx.font="700 18px system-ui";
    ctx.fillText("GAME COMPLETE",150,286);
    ctx.fillStyle="#9aabb6";ctx.font="11px ui-monospace,monospace";
    ctx.fillText(f.stats.pieces+" PLACEMENTS",150,310);
  }
}
function updateMetrics(r,suffix) {
  const stats=statsAt(r);
  $("score"+suffix).textContent=fmt(stats.score);
  $("lines"+suffix).textContent=fmt(stats.lines);
  $("pieces"+suffix).textContent=fmt(stats.pieces);
  $("tetrises"+suffix).textContent=fmt(stats.tetrises);
  $("well"+suffix).textContent=Math.round(100*stats.column_9_empty_fraction)+"%";
  const f=currentFrame(r);
  $("piece"+suffix).textContent="PIECE "+f.piece;
  const ended=state.index>=r.frames.length;
  $("state"+suffix).textContent=ended ? "FINISHED · "+r.frames.length+" MOVES" : "PLAYING";
}
function inputGroup(index) {
  return index<200 ? Math.floor(index/10) : 20+(index-200);
}
function nodePosition(layer,index) {
  if (layer===0) return [48,25+inputGroup(index)*8.55];
  if (layer===1) return [285+(index%8)*10.5,20+Math.floor(index/8)*13.8];
  if (layer===2) return [580+(index%4)*12,48+Math.floor(index/4)*20];
  return [846,132];
}
function groupedInputs(input) {
  const groups=[];
  for(let row=0;row<20;row++) {
    let sum=0;for(let x=0;x<10;x++)sum+=input[row*10+x];
    groups.push(sum/10);
  }
  for(let i=200;i<205;i++)groups.push(input[i]);
  return groups;
}
function drawNetwork(canvas,r,index,phase) {
  const ctx=canvas.getContext("2d"), width=900,height=260;
  ctx.clearRect(0,0,width,height);
  const f=r.frames[Math.min(index,r.frames.length-1)];
  const trace=f.trace;
  if (!trace) {
    ctx.fillStyle="#82919b";ctx.font="12px ui-monospace,monospace";ctx.fillText("No neural inference trace in this recording.",40,120);return;
  }
  ctx.font="10px ui-monospace,monospace";ctx.fillStyle="#82919b";ctx.textAlign="center";
  [["INPUT",48],["HIDDEN 1",322],["HIDDEN 2",598],["OUTPUT",846]].forEach(([label,x])=>ctx.fillText(label,x,12));
  ctx.fillStyle="#53636f";ctx.font="8px ui-monospace,monospace";
  ctx.fillText("205 FEATURES",48,252);ctx.fillText("128 NEURONS",322,252);ctx.fillText("32 NEURONS",598,252);ctx.fillText("MOVE SCORE",846,252);
  const input=groupedInputs(trace.layers[0]);
  const layers=[input,trace.layers[1],trace.layers[2],[f.candidates[f.selected][3]]];
  for(let layer=0;layer<3;layer++) {
    const edges=trace.edges[layer];
    const max=Math.max(1e-12,...edges.map(e=>Math.abs(e[3])));
    for(const edge of edges) {
      const src=edge[0],dst=edge[1],contribution=edge[3];
      const p1=nodePosition(layer,src),p2=nodePosition(layer+1,dst);
      const strength=Math.abs(contribution)/max;
      ctx.beginPath();ctx.moveTo(p1[0],p1[1]);ctx.lineTo(p2[0],p2[1]);
      ctx.strokeStyle=contribution>=0?"#71e4cb":"#f18db5";
      ctx.globalAlpha=.10+.58*strength;ctx.lineWidth=.55+1.45*strength;ctx.stroke();
      const pulse=(phase*1.6+layer*.23)%1;
      ctx.beginPath();ctx.arc(p1[0]+(p2[0]-p1[0])*pulse,p1[1]+(p2[1]-p1[1])*pulse,1.8+strength,0,Math.PI*2);
      ctx.fillStyle=contribution>=0?"#a8ffe4":"#ffc0d6";ctx.globalAlpha=.18+.72*strength;ctx.fill();
    }
  }
  ctx.globalAlpha=1;
  layers.forEach((values,layer)=>{
    const max=Math.max(1e-12,...values.map(v=>Math.abs(v)));
    values.forEach((value,i)=>{
      const p=nodePosition(layer,i),strength=Math.sqrt(Math.abs(value)/max);
      const radius=layer===3?8:layer===2?3.5:2.7;
      ctx.beginPath();ctx.arc(p[0],p[1],radius+strength*(layer===3?2:1),0,Math.PI*2);
      ctx.fillStyle="#25343b";ctx.fill();
      ctx.beginPath();ctx.arc(p[0],p[1],Math.max(1.1,radius*strength),0,Math.PI*2);
      ctx.fillStyle=layer===3?"#d7ff9c":(layer===1?"#8ff0d1":"#a99cff");
      ctx.globalAlpha=.22+.78*strength;ctx.fill();ctx.globalAlpha=1;
    });
  });
}
function placementLabel(candidate) {
  return "R"+candidate[0]+" · COL "+(candidate[1]+1);
}
function renderCandidates(r,id) {
  const f=currentFrame(r), list=f.candidates.map((candidate,index)=>({candidate,index}))
    .sort((a,b)=>b.candidate[3]-a.candidate[3] || a.index-b.index).slice(0,3);
  const selected=f.candidates[f.selected];
  const root=$("candidates"+id);root.replaceChildren();
  list.forEach((item,rank)=>{
    const el=document.createElement("div");
    el.className="candidate"+(item.index===f.selected?" selected":"");
    const rankEl=document.createElement("span");rankEl.className="rank";rankEl.textContent=String(rank+1).padStart(2,"0");
    const move=document.createElement("span");move.className="move";move.textContent=placementLabel(item.candidate);
    const value=document.createElement("span");value.className="value";value.textContent=item.candidate[3].toFixed(3);
    el.append(rankEl,move,value);root.append(el);
  });
  $("picked"+id).textContent="SELECTED · "+placementLabel(selected);
}
function renderDecision() {
  const a=currentFrame(state.a),b=currentFrame(state.b);
  $("decisionPiece").textContent="CURRENT PIECE · "+a.piece;
  renderCandidates(state.a,"A");renderCandidates(state.b,"B");
  const ca=a.candidates[a.selected],cb=b.candidates[b.selected];
  const same=ca[0]===cb[0] && ca[1]===cb[1];
  $("decisionDiff").textContent=same ? "SAME PLACEMENT" : "DIFFERENT MOVES";
  $("decisionDiff").style.color=same?"var(--mint)":"var(--amber)";
}
function render() {
  if(!state.a || !state.b)return;
  const i=state.index,p=state.phase;
  drawBoard($("boardA"),state.a,i,p);
  drawBoard($("boardB"),state.b,i,p);
  drawNetwork($("netA"),state.a,i,p);
  drawNetwork($("netB"),state.b,i,p);
  updateMetrics(state.a,"A");updateMetrics(state.b,"B");
  $("decisionNameA").textContent=state.a.policy.version;
  $("decisionNameB").textContent=state.b.policy.version;
  renderDecision();
  $("stepLabel").textContent="Placement "+Math.min(i+1,TOTAL())+" / "+TOTAL();
  $("seek").value=String(i);
}
function seek(index) {
  if(!state.a)return;
  pause();state.index=Math.max(0,Math.min(TOTAL()-1,index));state.phase=1;render();
}
function tick(time) {
  if(!state.playing)return;
  const delta=Math.min(80,time-lastTime);lastTime=time;
  state.phase+=delta*state.speed/600;
  if(state.phase>=1) {
    if(state.index+1>=TOTAL()) {state.phase=1;pause();}
    else {state.index++;state.phase=0;}
  }
  render();
  if(state.playing)raf=requestAnimationFrame(tick);
}
$("play").addEventListener("click",()=>{
  if(!state.a)return;
  if(state.playing){pause();return;}
  if(state.index>=TOTAL()-1 && state.phase>=1){state.index=0;state.phase=0;}
  state.playing=true;$("play").textContent="Ⅱ";$("play").setAttribute("aria-label","Pause");
  lastTime=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);
});
$("restart").addEventListener("click",()=>{pause();state.index=0;state.phase=0;render();});
$("prev").addEventListener("click",()=>seek(state.index-1));
$("next").addEventListener("click",()=>seek(state.index+1));
$("seek").addEventListener("input",e=>seek(Number(e.target.value)));
$("speed").addEventListener("change",e=>{state.speed=Number(e.target.value);});
$("runA").addEventListener("change",loadPair);
$("runB").addEventListener("change",loadPair);
window.addEventListener("keydown",e=>{
  if(e.code==="Space" && !["INPUT","SELECT","BUTTON"].includes(document.activeElement?.tagName)){e.preventDefault();$("play").click();}
  if(e.code==="ArrowRight" && !["INPUT","SELECT"].includes(document.activeElement?.tagName))seek(state.index+1);
  if(e.code==="ArrowLeft" && !["INPUT","SELECT"].includes(document.activeElement?.tagName))seek(state.index-1);
});
async function init() {
  try {
    manifest=await readJson("data/manifest.json");
    const recordings=manifest.replays.filter(item=>/^Astra v[123]/.test(item.name));
    if(recordings.length<2)throw new Error("At least two Astra neural recordings are required.");
    for(const item of recordings) {
      $("runA").add(new Option(item.name,item.path));
      $("runB").add(new Option(item.name,item.path));
    }
    const a=recordings.find(item=>item.name.startsWith("Astra v1")) || recordings[0];
    const b=recordings.find(item=>item.name.startsWith("Astra v3")) || recordings[recordings.length-1];
    $("runA").value=a.path;$("runB").value=b.path;
    await loadPair();
  } catch(error) {
    $("syncStatus").textContent="Unable to initialize replay studio · "+error.message;
  }
}
init();

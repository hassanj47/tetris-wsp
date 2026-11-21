"use strict";
const $ = id => document.getElementById(id);
const colors = ["#11161b","#71d4d9","#f5d17d","#bf9ce4","#7cddb6","#ed917e","#87ade6","#ebb37b"];
const mint = "#74e3be", coral = "#ff947b";
let catalog=[], diffs=[], replay=null, peer=null, step=0, phase=1, playing=false, tab="signal", last=0;
let selection=0, alignment=0, lastStats=null;
const emptyStats={score:0,level:1,lines:0,tetrises:0,pieces:0,column_9_empty_fraction:0};
function displayedStats(r){
  const index=step-(phase<.9?1:0);
  return index<0?emptyStats:r.frames[Math.min(index,r.frames.length-1)].stats;
}
const fmt=n=>Number(n).toLocaleString("en",{maximumFractionDigits:3});
function option(value,name){return new Option(name,value)}
function validate(r){
  if(r.schema_version!==1 || !r.config || !r.policy || !r.piece_ids || !Array.isArray(r.frames) || !r.frames.length)
    throw Error("Expected a nonempty schema 1 replay.");
  for(const f of r.frames){
    if(![f.before,f.after].every(b=>b?.length===20 && b.every(row=>row?.length===10)) ||
       !f.candidates?.[f.selected] || !f.stats || f.cells?.length!==4 ||
       (r.policy.kind==="neural" && !(f.neural?.x?.length===205 && f.neural.h1?.length===128 &&
        f.neural.h2?.length===32 && f.neural.edges?.length===3))) throw Error("Invalid replay frame.");
  }
  return r;
}
async function fetchJSON(url){
  const response=await fetch(url);
  if(!response.ok)throw Error("Could not open "+url);
  return response.json();
}
async function get(entry){
  if(!entry.data)entry.data=validate(await fetchJSON(entry.path));
  return entry.data;
}
function setPlaying(on){playing=on;$("play").textContent=on?"Ⅱ Pause":"▶ Play";last=0}
function total(){return Math.max(replay.frames.length,tab==="compare" && peer?peer.frames.length:0)}
function seek(n,p=1){step=Math.max(0,Math.min(total()-1,n));phase=p;$("timeline").value=step;render(true)}
async function align(){
  const token=++alignment;
  peer=null;
  if($("other").value!==""){
    const r=await get(catalog[+$("other").value]);
    if(token!==alignment)return;
    if(r.seed===replay.seed && r.config.cap===replay.config.cap && r.config.rules===replay.config.rules)peer=r;
  }
  $("timeline").max=total()-1;seek(step,phase);
}
async function select(){
  const token=++selection;
  setPlaying(false);
  const index=+$("source").value, r=await get(catalog[index]);
  if(token!==selection)return;
  replay=r;step=0;phase=1;
  $("seed").textContent="Seed "+r.seed;
  $("kind").textContent=r.fixture?"Test fixture":r.policy.version;
  $("provenance").textContent=(r.fixture?"Synthetic visualization fixture · ":r.policy.kind==="neural"?"Recorded neural inference · ":"Recorded baseline · ")+r.policy.version+
    (r.policy.sha256?" · SHA-256 "+r.policy.sha256.slice(0,12):"");
  const others=catalog.flatMap((e,i)=>i!==index && e.seed===r.seed && e.cap===r.config.cap && e.rules===r.config.rules?[option(i,e.name)]:[]);
  $("other").replaceChildren(...others);
  await align();
}
function block(ctx,x,y,size,color,ghost=false){
  ctx.fillStyle=color;ctx.strokeStyle=color;
  if(ghost){ctx.globalAlpha=.55;ctx.strokeRect(x+2,y+2,size-4,size-4);ctx.globalAlpha=1;return}
  ctx.fillRect(x+1,y+1,size-2,size-2);
  ctx.fillStyle="#ffffff38";ctx.fillRect(x+2,y+1,size-4,2);
}
function board(canvas,r,f,p){
  const ctx=canvas.getContext("2d"),s=canvas.width/10;
  ctx.fillStyle=colors[0];ctx.fillRect(0,0,canvas.width,canvas.height);
  const settled=p>=.90, grid=settled?f.after:f.before;
  grid.forEach((row,y)=>row.forEach((v,x)=>{
    ctx.strokeStyle="#212a31";ctx.strokeRect(x*s,y*s,s,s);
    if(v)block(ctx,x*s,y*s,s,colors[v]);
  }));
  if(settled)return;
  const color=colors[r.piece_ids[f.piece]],m=f.candidates[f.selected];
  f.cells.forEach(([y,x])=>block(ctx,x*s,y*s,s,color,true));
  const slide=Math.min(1,p/.30),fall=Math.min(1,Math.max(0,(p-.3)/.46));
  const cx=f.cells.reduce((a,c)=>a+c[1]+.5,0)/4, cy=f.cells.reduce((a,c)=>a+c[0]+.5,0)/4;
  ctx.save();ctx.translate(((4.5-cx)*(1-slide)+cx)*s,(cy-(m.y+1)*(1-fall*fall))*s);
  ctx.rotate(-m.rotation*Math.PI/2*(1-slide));
  f.cells.forEach(([y,x])=>block(ctx,(x-cx)*s,(y-cy)*s,s,color));ctx.restore();
  if(p>.76 && f.rows.length){
    ctx.fillStyle="rgba(255,248,218,"+Math.sin((p-.76)/.14*Math.PI)*.8+")";
    f.rows.forEach(y=>ctx.fillRect(0,y*s,s*10,s));
  }
}
function diagram(f,p){
  const canvas=$("net"),ctx=canvas.getContext("2d"),n=f.neural;
  ctx.clearRect(0,0,840,350);
  ctx.font="14px monospace";ctx.textAlign="center";ctx.fillStyle="#bac5c9";
  if(!n){ctx.fillText("Baseline decision · no neural inference",420,175);return}
  const layers=[n.x,n.h1,n.h2,[f.candidates[f.selected].score]];
  const spots=[
    i=>i<200?[60+(i%10)*6,82+Math.floor(i/10)*7]:[64+(i-200)*11,238],
    i=>[304+(i%8)*9,72+Math.floor(i/8)*13],
    i=>[550+(i%4)*12,104+Math.floor(i/4)*18],
    ()=>[756,168]
  ];
  n.edges.forEach((edges,d)=>edges.forEach((e,i)=>{
    const [x,y]=spots[d](e.src),[u,v]=spots[d+1](e.dst),mid=(u+x)/2;
    ctx.strokeStyle=e.value>=0?mint:coral;ctx.globalAlpha=.13+.48*(1-i/Math.max(1,edges.length));
    ctx.lineWidth=i<3?1.8:1;ctx.beginPath();ctx.moveTo(x,y);ctx.bezierCurveTo(mid,y,mid,v,u,v);ctx.stroke();
    const t=Math.min(1,Math.max(0,p*4-d));
    if(i<7 && t>0 && t<1){const k=1-t;ctx.fillStyle=ctx.strokeStyle;ctx.globalAlpha=.9;
      ctx.beginPath();ctx.arc(k**3*x+3*k*t*mid+t**3*u,k*k*(1+2*t)*y+t*t*(3-2*t)*v,2.6,0,7);ctx.fill()}
  }));
  ctx.globalAlpha=1;
  const centers=[86,335,568,756];
  layers.forEach((a,d)=>{
    const max=Math.max(1e-20,...a.map(Math.abs));
    a.forEach((v,i)=>{
      const [x,y]=spots[d](i),strength=Math.sqrt(Math.abs(v)/max);
      ctx.fillStyle=v<0?coral:mint;
      if(d===3){ctx.strokeStyle="#47665c";ctx.lineWidth=1;ctx.beginPath();ctx.arc(x,y,17,0,7);ctx.stroke()}
      ctx.globalAlpha = v ? .24 + .76*strength : .15;
      ctx.beginPath();
      if(d===0)ctx.rect(x-2,y-2,4.4,4.4);
      else ctx.arc(x,y,d===3?8:d===1?2.7:3.8,0,7);
      ctx.fill();
    });
    ctx.globalAlpha=1;ctx.fillStyle="#e4ebe9";ctx.font="15px monospace";
    ctx.fillText(["Input","Hidden 1","Hidden 2","Score"][d],centers[d],300);
    ctx.fillStyle="#8f9da5";ctx.font="12px monospace";
    ctx.fillText(["200 + 5","128 ReLU","32 ReLU","1 linear"][d],centers[d],322);
  });
}
function table(head,rows,chosen=-1){
  const t=document.createElement("table");
  [head,...rows].forEach((row,i)=>{
    const tr=t.insertRow();if(i-1===chosen)tr.className="sel";
    row.forEach(v=>{const c=document.createElement(i?"td":"th");c.textContent=v;tr.append(c)});
  });return t;
}
function comparison(){
  if(!peer){$("second").hidden=true;$("comparison").textContent="";$("compareNote").textContent="Open a second recording with the same seed and rules.";return}
  $("second").hidden=false;
  const f=peer.frames[Math.min(step,peer.frames.length-1)],a=replay.policy.sha256,b=peer.policy.sha256;
  const diff=diffs.find(d=>a && b && ((d.before===a && d.after===b)||(d.before===b && d.after===a)));
  const change=a && a===b?"0%":diff?fmt(diff.percent)+"%":"unavailable";
  $("compareNote").textContent="Primary network: "+replay.policy.version+" · Changed weights: "+change;
  board($("second"),peer,f,step>=peer.frames.length?1:phase);
  $("comparison").textContent=peer.policy.version+" · "+summary(displayedStats(peer));
}
function summary(s){return s.pieces+" pieces · "+s.lines+" lines · "+s.tetrises+" tetrises · well empty "+fmt(100*s.column_9_empty_fraction)+"%"}
function render(detail){
  if(!replay)return;
  const f=replay.frames[Math.min(step,replay.frames.length-1)],p=step>=replay.frames.length?1:phase,m=f.candidates[f.selected];
  board($("board"),replay,f,p);
  if(tab==="signal")diagram(f,p);
  if(tab==="compare")comparison();
  const settled=displayedStats(replay);
  if(!detail && lastStats===settled)return;
  lastStats=settled;
  const stats={Score:settled.score,Level:settled.level,Lines:settled.lines,Tetrises:settled.tetrises,Pieces:settled.pieces};
  const list=$("stats");list.replaceChildren();
  Object.entries(stats).forEach(([k,v])=>{const dt=document.createElement("dt"),dd=document.createElement("dd");dt.textContent=k;dd.textContent=fmt(v);list.append(dt,dd)});
  const ctx=$("piece").getContext("2d");ctx.clearRect(0,0,120,64);
  const top=Math.min(...f.cells.map(c=>c[0])),left=Math.min(...f.cells.map(c=>c[1]));
  f.cells.forEach(([y,x])=>block(ctx,(x-left)*15,2+(y-top)*15,15,colors[replay.piece_ids[f.piece]]));
  $("decision").textContent=tab==="compare"?summary(settled):f.piece+" piece · rotation "+m.rotation+" · column "+m.x;
  $("position").textContent=(step+1)+" / "+total();$("value").textContent=fmt(m.score);$("count").textContent=f.candidates.length;
  $("active").textContent=f.neural?[...f.neural.h1,...f.neural.h2].filter(v=>v>0).length+" / 160":"—";
  if(tab==="features"){
    const label=document.createElement("p");
    label.textContent=f.after.flat().filter(Boolean).length+" occupied cells · clear bits "+[0,1,2,3,4].map(i=>+(i===f.rows.length)).join(" ");
    $("features").replaceChildren(label,table(["Candidate","Rotation","Column","Score"],f.candidates.map((c,i)=>[i,c.rotation,c.x,fmt(c.score)]),f.selected));
  }
  if(tab==="weights")$("weights").replaceChildren(replay.tensors?table(["Tensor","Shape","Nonzero","Min","Max"],Object.entries(replay.tensors).map(([k,v])=>[k,v.shape.join(" × "),v.nonzero,fmt(v.min),fmt(v.max)])):"Baseline policy · no weight tensors.");
}
function frame(t){
  if(playing && replay){
    phase+=last?(t-last)*Number($("speed").value)/1300:0;last=t;
    if(phase>=1){
      if(step+1>=total()){setPlaying(false);seek(step,1)}
      else seek(step+1,0);
    }else render(false);
  }
  requestAnimationFrame(frame);
}
function guard(fn){return async(...args)=>{try{$("error").textContent="";await fn(...args)}catch(e){setPlaying(false);$("error").textContent=e.message}}}
$("play").onclick=()=>{if(!replay)return;if(!playing && phase===1)seek(step===total()-1?0:step,0);setPlaying(!playing)};
$("prev").onclick=()=>{if(replay){setPlaying(false);seek(step-1)}};
$("next").onclick=()=>{if(replay){setPlaying(false);seek(step+1)}};
$("timeline").oninput=e=>{if(replay){setPlaying(false);seek(+e.target.value)}};
$("source").onchange=guard(select);$("other").onchange=guard(align);
document.querySelectorAll("[data-tab]").forEach(btn=>btn.onclick=()=>{
  tab=btn.dataset.tab;
  document.querySelectorAll("[data-tab]").forEach(b=>{b.classList.toggle("active",b===btn);$(b.dataset.tab).hidden=b!==btn});
  if(replay){$("timeline").max=total()-1;seek(step,phase)}
});
$("load").onclick=()=>$("file").click();
$("file").onchange=guard(async e=>{
  let first=catalog.length;
  for(const file of e.target.files){
    const r=JSON.parse(await file.text());
    if(r.before && r.after && typeof r.percent==="number"){diffs.push(r);continue}
    validate(r);
    const name=r.policy.version+" · "+file.name;
    catalog.push({name,data:r,seed:r.seed,cap:r.config.cap,rules:r.config.rules});
    $("source").add(option(catalog.length-1,name));
  }
  if(catalog.length>first){$("source").value=first;await select()}else if(replay)render(true);
  e.target.value="";
});
guard(async()=>{
  const manifest=await fetchJSON("data/manifest.json");
  catalog=manifest.replays;diffs=manifest.diffs||[];
  $("source").replaceChildren(...catalog.map((e,i)=>option(i,e.name)));
  await select();
})() ;
requestAnimationFrame(frame);

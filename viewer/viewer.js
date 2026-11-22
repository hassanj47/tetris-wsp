import {validateReplay} from "./replay.mjs";

const $ = id => document.getElementById(id);
const colors = ['#101619','#69dacf','#e4c37c','#b99ae8','#9cce8c','#e39199','#88ace5','#eca778'];
const ids = ' IOTSZJL';
const state = {a:null,b:null,index:0,phase:1,playing:false,mode:'network',speed:1};
let manifest, ticket=0, last=0;
const cache=new Map();
const frame = r => r.frames[Math.min(state.index,r.frames.length-1)];
const total = () => Math.max(state.a.frames.length,state.b?.frames.length||0);
const ease = t => t*t*(3-2*t);
async function json(path) {
  const response=await fetch(path);
  if(!response.ok) throw Error('Unable to read '+path);
  return response.json();
}
async function recording(path) {
  if(!cache.has(path)){
    const r=await json('data/'+path);
    cache.set(path,validateReplay(r));
  }
  return cache.get(path);
}
function compatible(a,b){
  return a.seed===b.seed && ['rules','bag','cap','board'].every(k=>JSON.stringify(a.config[k])===JSON.stringify(b.config[k]));
}
async function load(){
  const token=++ticket;
  pause();
  try{
    const a=await recording($('recording').value);
    let b=$('compare').value ? await recording($('compare').value) : null;
    if(token!==ticket)return;
    let message='';
    if(b && !compatible(a,b)){message='Comparison requires matching seeds and rules. ';b=null;$('compare').value='';}
    const diff=b && manifest.comparisons?.find(d=>[a.policy.sha256,b.policy.sha256].sort().join('/')===[d.before,d.after].sort().join('/'));
    const opening = !state.a && !b && a.policy.fixture;
    Object.assign(state,{a,b,index:opening?Math.min(7,a.frames.length-1):0,phase:opening?1:0});
    $('seed').textContent='Seed '+a.seed;
    $('kind').textContent=a.policy.fixture?'Synthetic fixture':a.policy.version;
    $('status').textContent=message+(a.policy.fixture?'Visualization fixture · recorded inference from synthetic weights':a.policy.type==='neural'?'Recorded neural inference':'Recorded baseline gameplay')+(b?' · '+(diff?diff.percent.toFixed(3)+'% of weights changed':'Paired playback'):'');
    $('games').classList.toggle('paired',!!b);
    $('games').replaceChildren(...[a,b].filter(Boolean).map(gamePanel));
    $('seek').max=total()-1;
    render();
  }catch(err){if(token===ticket)$('status').textContent=err.message;}
}
function gamePanel(r){
  const el=document.createElement('div');el.className='game';
  const board=document.createElement('canvas');board.width=300;board.height=600;board.className='board';board.setAttribute('aria-label',r.policy.version+' playfield');
  const metrics=document.createElement('div');metrics.className='metrics';
  el.append(board,metrics);return el;
}
function cell(ctx,x,y,id,alpha=1,outline=false){
  const color=colors[id];ctx.globalAlpha=alpha;ctx.fillStyle=color;ctx.strokeStyle=color;
  if(outline){ctx.lineWidth=1.7;ctx.strokeRect(x*30+3,y*30+3,24,24);}
  else{ctx.fillRect(x*30+1.5,y*30+1.5,27,27);ctx.fillStyle='#ffffff34';ctx.fillRect(x*30+2,y*30+2,26,3);}
  ctx.globalAlpha=1;
}
function drawGame(el,r){
  const f=frame(r), [rot,x,y]=f.candidates[f.selected], id=ids.indexOf(f.piece);
  const phase=state.index>=r.frames.length?1:state.phase;
  const ctx=el.firstChild.getContext('2d');
  ctx.fillStyle=colors[0];ctx.fillRect(0,0,300,600);ctx.strokeStyle='#232d30';ctx.lineWidth=.8;
  for(let i=0;i<=20;i++){ctx.beginPath();ctx.moveTo(0,i*30);ctx.lineTo(300,i*30);ctx.stroke();}
  for(let i=0;i<=10;i++){ctx.beginPath();ctx.moveTo(i*30,0);ctx.lineTo(i*30,600);ctx.stroke();}
  (phase>=.94?f.after:f.before).forEach((row,iy)=>row.forEach((v,ix)=>{if(v)cell(ctx,ix,iy,v);}));
  if(phase<.94){
    const turn=ease(Math.min(1,phase/.36));
    const fall=ease(Math.max(0,Math.min(1,(phase-.36)/.43)));
    const target=r.shapes[f.piece][rot],spawn=r.shapes[f.piece][0];
    // Rotate in screen coordinates before descending; normalize to the final bounding box.
    const angle=turn*rot*Math.PI/2;
    const points=spawn.map(([sx,sy])=>[sx*Math.cos(angle)-sy*Math.sin(angle),sx*Math.sin(angle)+sy*Math.cos(angle)]);
    const minX=Math.min(...points.map(p=>p[0])),minY=Math.min(...points.map(p=>p[1]));
    target.forEach(([dx,dy])=>cell(ctx,x+dx,y+dy,id,.6,true));
    points.forEach(([dx,dy])=>cell(ctx,(1-turn)*3+turn*x+dx-minX,fall*y+dy-minY,id));
    if(phase>.79){ctx.fillStyle='rgba(241,255,210,'+(1-(phase-.79)/.15)+')';f.cleared.forEach(row=>ctx.fillRect(0,row*30,300,30));}
  }
}
function updateMetrics(el,r){
  const index=Math.min(state.index,r.frames.length-1), committed=state.phase>=.94 || state.index>=r.frames.length;
  const stats=r.frames[index-(committed?0:1)]?.stats||{score:0,lines:0,level:1,pieces:0,tetrises:0,column_9_empty_fraction:0};
  const data=[['Score',stats.score],['Lines / level',stats.lines+' / '+stats.level],['Pieces',stats.pieces],['Tetrises',stats.tetrises]];
  if(state.b)data.push(['Well empty',(100*stats.column_9_empty_fraction).toFixed(0)+'%']);
  const box=el.lastChild;box.replaceChildren();
  if(state.b){const h=document.createElement('h3');h.textContent=r.policy.version;box.append(h);}
  for(const [name,value] of data){
    const d=document.createElement('div'),s=document.createElement('small'),v=document.createElement('b');
    s.textContent=name.toUpperCase();v.textContent=value;if(name==='Score')v.className='big';d.append(s,v);box.append(d);
  }
  const d=document.createElement('div');d.innerHTML='<small>UPCOMING</small><div class="pieces"></div>';
  for(const f of r.frames.slice(index+1,index+4)){const tag=document.createElement('span');tag.textContent=f.piece;tag.style.color=colors[ids.indexOf(f.piece)];d.lastChild.append(tag);}
  if(!d.lastChild.childElementCount)d.lastChild.textContent='—';
  box.append(d);
}
function nodePosition(layer,i){
  if(layer===0){const g=i<200?Math.floor(i/10):20+i-200;return [55+(g%2)*14,55+Math.floor(g/2)*18];}
  if(layer===1)return [234+(i%8)*12,49+Math.floor(i/8)*15];
  if(layer===2)return [478+(i%4)*14,82+Math.floor(i/4)*23];
  return [694,164];
}
function drawNetwork(f){
  const canvas=$('graph'),ctx=canvas.getContext('2d'),ratio=Math.min(window.devicePixelRatio||1,2);
  if(canvas.width!==760*ratio){canvas.width=760*ratio;canvas.height=340*ratio;}
  ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,760,340);
  ctx.font='12px monospace';ctx.textAlign='center';ctx.fillStyle='#acb8b2';
  ['Input','Hidden 1','Hidden 2','Output'].forEach((s,i)=>ctx.fillText(s,[63,277,500,694][i],21));
  ['205 inputs','128 ReLU','32 ReLU','1 scalar'].forEach((s,i)=>ctx.fillText(s,[63,277,500,694][i],311));
  const trace=f.trace;
  if(!trace){ctx.fillText('Baseline policy · no neural inference',380,165);return;}
  const [input,h1,h2]=trace.layers;
  const grouped=Array.from({length:20},(_,i)=>input.slice(i*10,i*10+10).reduce((a,b)=>a+b,0)/10).concat(input.slice(200));
  trace.edges.forEach((edges,l)=>{
    const max=Math.max(1e-12,...edges.map(e=>Math.abs(e[3])));
    for(const [src,dst,,v] of edges){
      const [x,y]=nodePosition(l,src),[xx,yy]=nodePosition(l+1,dst);
      const strength=Math.abs(v)/max, color=v>0?'#7be7cf':'#ed8eb7';
      ctx.strokeStyle=color;ctx.lineWidth=.45+1.15*strength;ctx.globalAlpha=.12+.46*strength;
      ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(xx,yy);ctx.stroke();
      const t=(state.phase*3.4-l);
      if(t>=0 && t<=1){ctx.globalAlpha=.8;ctx.fillStyle=color;ctx.beginPath();ctx.arc(x+(xx-x)*t,y+(yy-y)*t,2,0,Math.PI*2);ctx.fill();}
    }
  });
  ctx.globalAlpha=1;
  [grouped,h1,h2,[f.candidates[f.selected][3]]].forEach((values,l)=>{
    const max=Math.max(1e-12,...values.map(Math.abs));
    values.forEach((v,i)=>{
      const [x,y]=nodePosition(l,l===0 && i<20?i*10:l===0?180+i:i);
      ctx.fillStyle='#293332';ctx.beginPath();ctx.arc(x,y,l===3?12:l===2?4.5:3.7,0,2*Math.PI);ctx.fill();
      ctx.globalAlpha=Math.sqrt(Math.abs(v)/max);ctx.fillStyle=l===3?'#d5fb84':'#92ebcc';ctx.fill();ctx.globalAlpha=1;
    });
  });
}
function details(f){
  const [,x,,score]=f.candidates[f.selected];
  $('placement').textContent=f.piece+' · R'+f.candidates[f.selected][0]+' · col '+x;
  $('score').textContent=score.toFixed(4);
  $('readout').textContent=state.a.policy.version+'  /  '+f.candidates.length+' legal placements  /  '+(f.trace?'Highest score selected':'Baseline decision');
  $('network').hidden=state.mode!=='network';$('detail').hidden=state.mode==='network';
  if(state.mode==='features'){
    const occupancy=f.after.map(row=>row.map(v=>v?'■':'·').join('')).join('\n');
    $('detail').textContent='Board occupancy · post-clear\n'+occupancy+'\nClear-count input  '+[0,1,2,3,4].map(n=>+(n===f.cleared.length)).join(' ')+'\n\nCandidates by score\n'+f.candidates.map(([r,x,y,s],i)=>({r,x,y,s,i})).sort((a,b)=>b.s-a.s||a.i-b.i).map(c=>(c.i===f.selected?'→ ':'  ')+'R'+c.r+'  col '+c.x+'  '+c.s.toFixed(5)).join('\n');
  }else if(state.mode==='weights'){
    $('detail').textContent=f.trace?'Strongest active connections · selected placement\n\n'+f.trace.edges.map((edges,l)=>'W'+(l+1)+'    source → target      weight     contribution\n'+edges.map(([i,j,w,c])=>String(i).padStart(6)+' → '+String(j).padEnd(6)+w.toFixed(5).padStart(10)+c.toFixed(5).padStart(15)).join('\n')).join('\n\n'):'The baseline uses no neural weights.';
  }
}
let previousKey='';
function render(){
  if(!state.a)return;
  const key=[ticket,state.index,state.phase>=.94,state.mode].join('-');
  [state.a,state.b].filter(Boolean).forEach((r,i)=>{const el=$('games').children[i];drawGame(el,r);if(key!==previousKey)updateMetrics(el,r);});
  if(key!==previousKey){details(frame(state.a));$('counter').value=(state.index+1)+' / '+total();$('seek').value=state.index;}
  if(state.mode==='network')drawNetwork(frame(state.a));
  previousKey=key;
}
function pause(){state.playing=false;$('play').textContent='▶';$('play').setAttribute('aria-label','Play');}
function tick(time){
  if(!state.playing)return;
  state.phase+=(time-last)*state.speed/1300;last=time;
  if(state.phase>=1){if(state.index+1>=total()){state.phase=1;pause();}else{state.index++;state.phase=0;}}
  render();if(state.playing)raf=requestAnimationFrame(tick);
}
let raf=0;
$('play').onclick=()=>{
  if(!state.a)return;
  if(state.playing){pause();return;}
  if(state.index===total()-1 && state.phase===1){state.index=0;state.phase=0;}
  state.playing=true;$('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause');last=performance.now();
  cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);
};
function seek(i){if(!state.a)return;pause();state.index=Math.max(0,Math.min(total()-1,i));state.phase=1;render();}
$('prev').onclick=()=>seek(state.index-1);$('next').onclick=()=>seek(state.index+1);
$('seek').oninput=e=>seek(+e.target.value);$('speed').onchange=e=>{state.speed=+e.target.value;};
document.querySelectorAll('[data-mode]').forEach(btn=>btn.onclick=()=>{
  state.mode=btn.dataset.mode;document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',b===btn));render();
});
let importCount=0;
$('import').onclick=()=>$('file').click();
$('file').onchange=async event=>{
  const file=event.target.files[0];
  event.target.value='';
  if(!file)return;
  try{
    const replay=validateReplay(JSON.parse(await file.text()));
    const key='local:'+ ++importCount;
    cache.set(key,replay);
    for(const id of ['recording','compare']) $(id).add(new Option(file.name,key));
    $('recording').value=key;
    await load();
  }catch(err){$('status').textContent='Import failed · '+err.message;}
};
$('recording').onchange=load;$('compare').onchange=load;
try{
  manifest=await json('data/manifest.json');
  for(const r of manifest.replays){for(const id of ['recording','compare'])$(id).add(new Option(r.name,r.path));}
  await load();
}catch(err){$('status').textContent=err.message;}

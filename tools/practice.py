"""Fixed, bounded practice feedback for Astra v3."""
import argparse, json
from pathlib import Path
from statistics import mean, median
import numpy as np
from net.mlp import encode, forward, strongest
from net.spec import load, digest
from tetris.engine import play
from tetris.pieces import SHAPES

SEEDS={1:range(9000,9020),2:range(9020,9040),3:range(9040,9060)}
CONFIG={"rules":"vertical-drop-1","board":[20,10],"bag":"numpy-PCG64-seven-bag","cap":1000}
POINTS=(0,100,300,500,800)

def write(path,obj):
 p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,allow_nan=False,indent=2)+"\n",encoding="utf-8")

def game(seed,w,path,version,record=False):
 def choose(moves):
  x=encode(moves); h1,h2,s=forward(x,w); trace=None
  if record:
   i=int(np.argmax(s)); layers=[a[i] for a in (x,h1,h2)]
   trace={"layers":[a.tolist() for a in layers],"edges":[strongest(a,w[f"W{k}"]) for k,a in enumerate(layers,1)]}
  return s,trace
 counts=[0]*5; score=lines=pieces=hs=peak=well=0; frames=[]
 for before,piece,moves,scores,selected,trace in play(seed,1000,choose):
  m=moves[selected]; n=len(m.rows); score+=POINTS[n]*(1+lines//10); lines+=n; counts[n]+=1; pieces+=1
  filled=np.flatnonzero(m.board.any(axis=1)); height=20-int(filled[0]) if filled.size else 0
  hs+=height; peak=max(peak,height); well+=int(not m.board[:,9].any())
  if record:
   frames.append({"before":before.tolist(),"after":m.board.tolist(),"piece":piece,
    "candidates":[[a.rotation,a.x,a.y,float(v)] for a,v in zip(moves,scores)],
    "selected":selected,"cleared":m.rows,"trace":trace,
    "stats":{"pieces":pieces,"lines":lines,"level":1+lines//10,"score":score,
    "tetrises":counts[4],"column_9_empty_fraction":well/pieces}})
 g={"seed":seed,"score":score,"lines":lines,"pieces":pieces,"singles":counts[1],
 "doubles":counts[2],"triples":counts[3],"tetrises":counts[4],"capped":pieces==1000,
 "mean_stack_height":hs/max(1,pieces),"max_stack_height":peak,
 "column_9_empty_fraction":well/max(1,pieces)}
 r={"schema_version":1,"config":dict(CONFIG),"seed":seed,
 "policy":{"type":"neural","version":version,"implementation":"wsp-discovery-v3-1",
 "artifact":Path(path).name,"sha256":digest(path)},"game":g}
 if record:
  r.update(frames=frames,shapes={p:[[[int(x),int(y)] for x,y in rot] for rot in SHAPES[p]] for p in SHAPES})
 return r

def aggregate(gs):
 c={k:sum(g[k] for g in gs) for k in ("singles","doubles","triples","tetrises")}
 lines=sum(g["lines"] for g in gs); events=sum(c.values())
 return {"mean_score":mean(g["score"] for g in gs),"median_score":median(g["score"] for g in gs),
 "min_score":min(g["score"] for g in gs),"max_score":max(g["score"] for g in gs),
 "mean_lines":mean(g["lines"] for g in gs),"mean_pieces":mean(g["pieces"] for g in gs),
 "tetrises_per_game":c["tetrises"]/len(gs),"clear_events":c,
 "tetris_event_share":c["tetrises"]/max(1,events),"tetris_line_share":4*c["tetrises"]/max(1,lines),
 "cap_reached_percent":100*mean(g["capped"] for g in gs),
 "mean_stack_height":mean(g["mean_stack_height"] for g in gs),
 "max_stack_height":max(g["max_stack_height"] for g in gs),
 "column_9_empty_fraction":mean(g["column_9_empty_fraction"] for g in gs)}

def round_run(n,path,version,out):
 out=Path(out)
 if out.exists() and any(out.iterdir()): raise FileExistsError(f"Refusing to overwrite {out}")
 out.mkdir(parents=True,exist_ok=True); w=load(path)
 rs=[game(seed,w,path,version) for seed in SEEDS[n]]; gs=[r["game"] for r in rs]
 ordered=sorted(gs,key=lambda g:(g["score"],g["seed"]))
 picks=[("shortest-survival",min(gs,key=lambda g:(g["pieces"],g["score"],g["seed"]))),
 ("median-score",ordered[len(ordered)//2]),("highest-score",max(gs,key=lambda g:(g["score"],g["pieces"],-g["seed"])))]
 unique=[]; seen=set()
 for role,g in picks:
  if g["seed"] not in seen: unique.append((role,g)); seen.add(g["seed"])
 for role,g in ordered:
  if len(unique)==3: break
  if g["seed"] not in seen: unique.append(("additional-diagnostic",g)); seen.add(g["seed"])
 rd=out/"replays"; rd.mkdir()
 diagnostics=[]
 for role,g in unique:
  r=game(g["seed"],w,path,version,True); name=f"{role}-seed-{g['seed']}.json"; write(rd/name,r)
  diagnostics.append({"role":role,"seed":g["seed"],"path":f"replays/{name}"})
 stats=aggregate(gs); report={"protocol":"feedback-guided WSP v3","round":n,"version":version,
 "weight_sha256":digest(path),"config":CONFIG,"seeds":list(SEEDS[n]),"aggregate":stats,
 "games":gs,"diagnostic_replays":diagnostics,
 "note":"Three diagnostic replays are selected from this same 20-game batch; not additional samples."}
 write(out/"feedback.json",report)
 rows="\n".join(f"| {k} | {v} |" for k,v in stats.items())
 (out/"REPORT.md").write_text(f"# Astra v3 practice round {n}\n\n20 games, seeds {min(SEEDS[n])}-{max(SEEDS[n])}, cap 1000.\n\nWeight SHA-256: {digest(path)}\n\n| Metric | Result |\n|---|---:|\n{rows}\n\n## Diagnostic replays\n"+"\n".join(f"- {role}: seed {game['seed']} — {item['path']}" for (role,game),item in zip(unique,diagnostics))+"\n",encoding="utf-8")
 return report

def showcase(path,version,out):
 w=load(path); write(out,game(73,w,path,version,True))

def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
 q=sub.add_parser("round"); q.add_argument("--number",type=int,choices=(1,2,3),required=True); q.add_argument("--weights",required=True,type=Path); q.add_argument("--version",required=True); q.add_argument("--out-dir",required=True,type=Path)
 q=sub.add_parser("showcase"); q.add_argument("--weights",required=True,type=Path); q.add_argument("--version",required=True); q.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 if a.cmd=="round": round_run(a.number,a.weights,a.version,a.out_dir)
 else: showcase(a.weights,a.version,a.out)
if __name__=="__main__": main()

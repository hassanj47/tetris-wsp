from statistics import mean, median
from .simulation import parser, simulate, write

def aggregate(games):
    lines=[g["lines"] for g in games]
    composition={k:sum(g[k] for g in games) for k in ("singles","doubles","triples","tetrises")}
    t=composition["tetrises"]
    return dict(mean_lines=mean(lines),median_lines=median(lines),min_lines=min(lines),max_lines=max(lines),
        mean_pieces=mean(g["pieces"] for g in games),tetrises_per_game=t/len(games),
        line_clear_events=composition,tetris_event_share=t/max(1,sum(composition.values())),
        tetris_line_share=4*t/max(1,sum(lines)),cap_reached_percent=100*mean(g["cap_reached"] for g in games),
        column_9_empty_fraction=mean(g["column_9_empty_fraction"] for g in games))

def main():
    p=parser("Evaluate a placement policy on the supplied seeds")
    p.add_argument("--seeds",type=int,nargs="+",required=True)
    args=p.parse_args()
    games=[]
    for seed in args.seeds:
        metrics,metadata=simulate(args,seed)
        games.append(metrics)
    summary=aggregate(games)
    write(args.out,dict(policy=metadata["policy"],config=metadata["config"],games=games,aggregate=summary))
    fields=list(games[0])
    md=["# "+metadata["policy"]["version"],"",f"Piece cap {args.cap}. Artifact SHA-256 {metadata['policy']['sha256']}.","",
        "| Metric | Value |","|---|---:|",*[f"| {k} | {v} |" for k,v in summary.items()],
        "","## Per game","","| "+" | ".join(fields)+" |","|"+"---|"*len(fields)]
    md.extend("| "+" | ".join(str(g[k]) for k in fields)+" |" for g in games)
    args.out.with_suffix(".md").write_text("\n".join(md)+"\n")

if __name__=="__main__":
    main()

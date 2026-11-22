from statistics import mean, median
from .simulation import arguments, simulate, write_json


def aggregate(games):
    lines = [g["lines"] for g in games]
    counts = {k: sum(g[k] for g in games) for k in ("singles", "doubles", "triples", "tetrises")}
    return dict(mean_lines=mean(lines), median_lines=median(lines), min_lines=min(lines),
                max_lines=max(lines), mean_pieces=mean(g["pieces"] for g in games),
                tetrises_per_game=counts["tetrises"]/len(games), clear_events=counts,
                tetris_event_share=counts["tetrises"]/max(1,sum(counts.values())),
                tetris_line_share=4*counts["tetrises"]/max(1,sum(lines)),
                cap_percent=100*mean(g["capped"] for g in games),
                column_9_empty_fraction=mean(g["column_9_empty_fraction"] for g in games))


def main():
    parser = arguments("Evaluate a policy on explicitly supplied seeds")
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--cohort", choices=["development","refinement","held-out"], default="development")
    args = parser.parse_args()
    if len(set(args.seeds)) != len(args.seeds):
        parser.error("supply distinct seeds")
    runs = [simulate(args, seed) for seed in args.seeds]
    games = [r["game"] for r in runs]
    stats = aggregate(games)
    write_json(args.out, dict(policy=runs[0]["policy"], config=runs[0]["config"], cohort=args.cohort,
                              games=games, aggregate=stats))
    report = [f"# {runs[0]['policy']['version']} evaluation", "", f"{len(games)} games · {args.cohort}",
              "", "| Metric | Value |", "|---|---:|"]
    for name, value in stats.items():
        items = value.items() if isinstance(value, dict) else [(name, value)]
        report.extend(f"| {key} | {v:.6g} |" for key, v in items)
    args.out.with_suffix(".md").write_text("\n".join(report)+"\n")


if __name__ == "__main__":
    main()

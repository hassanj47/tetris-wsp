"""Seed-matched evaluation of frozen WSP Tetris controllers; no training or editing."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from statistics import mean, median
import numpy as np

from net.mlp import forward
from net.spec import load, digest
from tetris.rng import seven_bag
from tools.practice import CONFIG, game

ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / "evaluation" / "policies.json"
COHORT_FILE = ROOT / "evaluation" / "COHORT.json"
EXPECTED_SOURCE_BLOBS = {
  "tetris/engine.py": "e517ee90b95e03657ee406b43baeb373dbdecfdd",
  "tetris/moves.py": "e9579bc21d73e079a9ed1c16f1258c0ad027327a",
  "tetris/rng.py": "f112d4f2bc3d3955ca0b132b112575d232b6bfe9",
  "tetris/pieces.py": "3708b4425c18c53abc4544987c508454b4ce036c",
  "net/mlp.py": "48a62bb3d3abe802e3045fcdef4a9e254fffbab7",
  "net/spec.py": "a6185fc29bda196748009af1f7183c5449a326db",
  "tools/practice.py": "2b8929a4da54698b4d40b632bb55354d68c4e282"
}
CONTRASTS = [
    ("v3_final", "v3_initial", "PRIMARY: final v3 vs initial v3"),
    ("v3_final", "astra_v1", "final v3 vs v1"),
    ("v3_final", "astra_v2", "final v3 vs v2"),
    ("v3_r1", "v3_initial", "v3 revision 1 vs initial"),
    ("v3_r2", "v3_r1", "v3 revision 2 vs revision 1"),
    ("v3_final", "v3_r2", "v3 final vs revision 2"),
]
METRICS = ("score", "lines", "pieces")
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 20261125
OUT_DIR = ROOT / "evaluation" / "results" / "paired-v1"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def source_hashes():
    found = {}
    for rel, expected in EXPECTED_SOURCE_BLOBS.items():
        path = ROOT / rel
        actual = git_blob_sha(path)
        if actual != expected:
            raise ValueError(f"Runtime source changed: {rel}: expected {expected}, got {actual}")
        found[rel] = actual
    return found


def load_inputs():
    cohort = read_json(COHORT_FILE)
    policies = read_json(POLICY_FILE)
    seeds = cohort["seeds"]
    if cohort["count"] != 50 or len(seeds) != 50 or len(set(seeds)) != 50:
        raise ValueError("Expected exactly 50 unique committed seeds")
    if seeds != sorted(seeds) or any(not 100_000 <= int(s) <= 999_999 for s in seeds):
        raise ValueError("Invalid seed cohort")
    reserved = set(range(11, 14)) | {73} | set(range(9000, 9060)) | set(range(10000, 10020))
    if reserved.intersection(seeds):
        raise ValueError("Cohort overlaps a documented prior seed set")
    if len(policies) != 6 or len({p["id"] for p in policies}) != 6:
        raise ValueError("Expected six unique frozen policies")
    loaded = {}
    for p in policies:
        path = ROOT / p["artifact"]
        actual = digest(path)
        if actual != p["sha256"]:
            raise ValueError(f"Weight hash mismatch for {p['id']}: {actual}")
        w = load(path)
        label_path = ROOT / p["labels"]
        if hashlib.sha256(label_path.read_bytes()).hexdigest() != p["labels_sha256"]:
            raise ValueError(f"Label hash mismatch for {p['id']}")
        loaded[p["id"]] = (p, path, w)
    if CONFIG != {"rules": "vertical-drop-1", "board": [20, 10],
                  "bag": "numpy-PCG64-seven-bag", "cap": 1000}:
        raise ValueError("Practice runtime configuration changed")
    return cohort, policies, seeds, loaded


def piece_sequence_sha256(seed: int, cap: int = 1000) -> str:
    import itertools
    sequence = "".join(itertools.islice(seven_bag(seed), cap)).encode("ascii")
    return hashlib.sha256(sequence).hexdigest()


def aggregate(games: list[dict]) -> dict:
    clear_counts = {k: sum(g[k] for g in games)
                    for k in ("singles", "doubles", "triples", "tetrises")}
    total_lines = sum(g["lines"] for g in games)
    total_events = sum(clear_counts.values())
    scores = [g["score"] for g in games]
    lines = [g["lines"] for g in games]
    pieces = [g["pieces"] for g in games]
    return {
        "games": len(games),
        "mean_score": mean(scores), "median_score": median(scores),
        "score_sd_sample": float(np.std(scores, ddof=1)),
        "min_score": min(scores), "max_score": max(scores),
        "mean_lines": mean(lines), "median_lines": median(lines),
        "mean_pieces": mean(pieces), "median_pieces": median(pieces),
        "cap_games": sum(bool(g["capped"]) for g in games),
        "cap_rate_percent": 100 * mean(bool(g["capped"]) for g in games),
        "clear_events": clear_counts,
        "tetrises_per_game": clear_counts["tetrises"] / len(games),
        "tetris_event_share_percent": 100 * clear_counts["tetrises"] / max(1, total_events),
        "tetris_line_share_percent": 100 * 4 * clear_counts["tetrises"] / max(1, total_lines),
        "mean_game_mean_stack_height": mean(g["mean_stack_height"] for g in games),
        "max_observed_stack_height": max(g["max_stack_height"] for g in games),
        "mean_column_9_empty_fraction_percent": 100 * mean(g["column_9_empty_fraction"] for g in games),
    }


def bootstrap_mean_ci(differences: list[float], rng: np.random.Generator) -> list[float]:
    values = np.asarray(differences, dtype=np.float64)
    n = len(values)
    indices = rng.integers(0, n, size=(BOOTSTRAP_REPS, n))
    means = values[indices].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return [float(lo), float(hi)]


def paired_contrast(left: list[dict], right: list[dict], rng: np.random.Generator) -> dict:
    by_left = {g["seed"]: g for g in left}
    by_right = {g["seed"]: g for g in right}
    if set(by_left) != set(by_right):
        raise ValueError("Paired comparison seed sets differ")
    seeds = sorted(by_left)
    result = {}
    for metric in METRICS:
        diffs = [float(by_left[s][metric] - by_right[s][metric]) for s in seeds]
        result[metric] = {
            "mean_difference_left_minus_right": mean(diffs),
            "median_difference_left_minus_right": median(diffs),
            "bootstrap_95pct_ci_for_mean_difference": bootstrap_mean_ci(diffs, rng),
        }
    wins = sum(by_left[s]["score"] > by_right[s]["score"] for s in seeds)
    ties = sum(by_left[s]["score"] == by_right[s]["score"] for s in seeds)
    losses = len(seeds) - wins - ties
    result["score_win_tie_loss"] = {"left_wins": wins, "ties": ties, "right_wins": losses}
    return result


def run_evaluation():
    if OUT_DIR.exists():
        raise FileExistsError(f"Refusing to rerun or overwrite existing evaluation directory: {OUT_DIR}")
    cohort, policies, seeds, loaded = load_inputs()
    blobs = source_hashes()
    status = {
        "status": "started",
        "cohort_id": cohort["cohort_id"],
        "expected_games": len(seeds) * len(policies),
        "policy_ids": [p["id"] for p in policies],
        "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                         text=True, capture_output=True, check=True).stdout.strip(),
        "source_blobs": blobs,
        "note": "If interrupted, do not rerun this cohort automatically; inspect the status and report."
    }
    OUT_DIR.mkdir(parents=True)
    write_json(OUT_DIR / "RUN_STATUS.json", status)
    try:
        per_seed = []
        policy_games = {p["id"]: [] for p in policies}
        for seed in seeds:
            seq_hash = piece_sequence_sha256(int(seed), CONFIG["cap"])
            row = {"seed": int(seed), "piece_sequence_sha256": seq_hash, "outcomes": {}}
            for p in policies:
                path, weights = loaded[p["id"]][1], loaded[p["id"]][2]
                replay = game(int(seed), weights, path, p["name"], record=False)
                outcome = replay["game"]
                if outcome["seed"] != seed or outcome["pieces"] > CONFIG["cap"]:
                    raise ValueError(f"Unexpected game result for {p['id']} seed {seed}")
                row["outcomes"][p["id"]] = outcome
                policy_games[p["id"]].append(outcome)
            per_seed.append(row)
        aggregates = {p["id"]: aggregate(policy_games[p["id"]]) for p in policies}
        policy_lookup = {p["id"]: p for p in policies}
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        contrasts = []
        for left_id, right_id, label in CONTRASTS:
            contrasts.append({
                "label": label, "left": left_id, "right": right_id,
                "left_name": policy_lookup[left_id]["name"],
                "right_name": policy_lookup[right_id]["name"],
                "paired": paired_contrast(policy_games[left_id], policy_games[right_id], rng),
            })
        result = {
            "schema_version": 1,
            "protocol": "50-seed paired evaluation of six frozen controllers",
            "source_commit": status["source_commit"],
            "source_blobs": blobs,
            "config": CONFIG,
            "cohort": cohort,
            "policies": [{**p, "aggregate": aggregates[p["id"]]} for p in policies],
            "predeclared_contrasts": contrasts,
            "per_seed": per_seed,
            "interpretation_limit": (
                "Controllers were frozen before this cohort was evaluated. The cohort is held out "
                "from the documented strategy-development runs, but was selected after the policies "
                "were frozen rather than preregistered before authoring. Results estimate performance "
                "on this fixed cohort and do not prove universal superiority or explain causation."
            ),
        }
        write_json(OUT_DIR / "paired-evaluation.json", result)
        csv_path = OUT_DIR / "per-seed.csv"
        fields = ["seed", "piece_sequence_sha256", "policy_id", "policy_name",
                  "score", "lines", "pieces", "capped", "singles", "doubles",
                  "triples", "tetrises", "mean_stack_height", "max_stack_height",
                  "column_9_empty_fraction"]
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in per_seed:
                for p in policies:
                    g = row["outcomes"][p["id"]]
                    writer.writerow({"seed": row["seed"], "piece_sequence_sha256": row["piece_sequence_sha256"],
                                     "policy_id": p["id"], "policy_name": p["name"], **g})
        lines = [
            "# Seed-matched Tetris controller evaluation", "",
            f"**{len(seeds)} shared seeds × {len(policies)} frozen controllers = {len(seeds)*len(policies)} games.**",
            "", f"Source commit: `{status['source_commit']}`",
            "", "## Controller aggregates", "",
            "| Controller | Mean score | Median score | Mean lines | Mean pieces | Cap rate | Tetrises/game |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for p in policies:
            a = aggregates[p["id"]]
            lines.append(f"| {p['name']} | {a['mean_score']:.1f} | {a['median_score']:.1f} | "
                         f"{a['mean_lines']:.2f} | {a['mean_pieces']:.1f} | "
                         f"{a['cap_rate_percent']:.1f}% | {a['tetrises_per_game']:.2f} |")
        lines += ["", "## Predeclared paired contrasts", "",
                  "Positive differences favor the left-hand controller. Confidence intervals are paired bootstrap percentile intervals (20,000 resamples).",
                  "", "| Contrast | Mean score difference | 95% CI | Score W/T/L | Mean lines difference | Mean pieces difference |",
                  "|---|---:|---:|---:|---:|---:|"]
        for c in contrasts:
            s = c["paired"]["score"]
            ci = s["bootstrap_95pct_ci_for_mean_difference"]
            wtl = c["paired"]["score_win_tie_loss"]
            lines.append(f"| {c['label']} | {s['mean_difference_left_minus_right']:.1f} | "
                         f"[{ci[0]:.1f}, {ci[1]:.1f}] | "
                         f"{wtl['left_wins']}/{wtl['ties']}/{wtl['right_wins']} | "
                         f"{c['paired']['lines']['mean_difference_left_minus_right']:.2f} | "
                         f"{c['paired']['pieces']['mean_difference_left_minus_right']:.1f} |")
        lines += ["", "## Interpretation and limitations", "",
                  result["interpretation_limit"], "",
                  "All controllers received the same 50 seeded seven-bag piece sequences (identical full 1,000-piece sequence per seed; games may terminate earlier). "
                  "This is a paired simulation benchmark, not a real-world experiment. Secondary contrasts are descriptive; no multiple-comparison correction is applied.",
                  "", "Raw per-seed results are in `per-seed.csv` and `paired-evaluation.json`.",
                  ""]
        (OUT_DIR / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
        status["status"] = "complete"
        status["completed_games"] = len(seeds) * len(policies)
        status["result_file"] = "paired-evaluation.json"
        write_json(OUT_DIR / "RUN_STATUS.json", status)
    except BaseException as exc:
        status["status"] = "failed"
        status["error"] = f"{type(exc).__name__}: {exc}"
        write_json(OUT_DIR / "RUN_STATUS.json", status)
        raise
    print(f"Completed {len(seeds) * len(policies)} games. Report: {OUT_DIR / 'REPORT.md'}")


def verify_only():
    cohort, policies, seeds, loaded = load_inputs()
    blobs = source_hashes()
    print(f"Verified {len(policies)} weight archives and labels; {len(seeds)} fixed seeds; "
          f"{len(blobs)} pinned runtime files. No games executed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify-only", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify_only()
    else:
        run_evaluation()


if __name__ == "__main__":
    main()

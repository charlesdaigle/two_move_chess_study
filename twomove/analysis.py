"""Aggregate JSONL game records into balance statistics and reports.

Reads every *.jsonl in a results directory (shards merge implicitly), groups by
point_id, and reports the double-mover's score with Wilson 95% CI, an Elo-equivalent,
termination reasons and game lengths. Emits markdown and CSV.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys
from collections import defaultdict
from typing import Dict, List


def wilson_ci(successes: float, n: int, z: float = 1.96):
    """Wilson interval; `successes` may be fractional (draws = 0.5)."""
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def elo(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return 400.0 * math.log10(p / (1 - p))


def load_records(results_dir: str) -> List[Dict]:
    recs = []
    for path in sorted(glob.glob(os.path.join(results_dir, "*.jsonl"))):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return recs


def summarize(recs: List[Dict]) -> List[Dict]:
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for r in recs:
        if r.get("double_score") is None:
            continue
        groups[r["point_id"]].append(r)
    rows = []
    for pid, rs in sorted(groups.items()):
        n = len(rs)
        s = sum(r["double_score"] for r in rs)
        wins = sum(1 for r in rs if r["double_score"] == 1.0)
        losses = sum(1 for r in rs if r["double_score"] == 0.0)
        draws = n - wins - losses
        p = s / n
        lo, hi = wilson_ci(s, n)
        reasons = defaultdict(int)
        for r in rs:
            reasons[r["reason"]] += 1
        lengths = sorted(r.get("n_rounds", 0) for r in rs)
        rows.append({
            "point_id": pid,
            "label": rs[0].get("label", ""),
            "n": n, "wins": wins, "draws": draws, "losses": losses,
            "score": round(p, 4),
            "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
            "elo": round(elo(p), 1),
            "draw_rate": round(draws / n, 3),
            "median_rounds": lengths[n // 2] if n else 0,
            "reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
            "balanced": lo >= 0.40 and hi <= 0.60 and 0.45 <= p <= 0.55,
        })
    rows.sort(key=lambda r: abs(r["score"] - 0.5))
    return rows


def markdown_report(rows: List[Dict]) -> str:
    lines = [
        "# Sweep results (double-mover score)",
        "",
        "Sorted by distance from 50%. `balanced` = Wilson CI within [0.40,0.60] and "
        "score within [0.45,0.55] (spec.md criterion, tau=0.05 needs N>~384).",
        "",
        "| label | point | N | W/D/L | score | 95% CI | Elo | med.len | terminations | balanced |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        term = ", ".join(f"{k}:{v}" for k, v in r["reasons"].items())
        pid = r["point_id"].replace("|", "\\|")
        lines.append(
            f"| {r['label']} | `{pid}` | {r['n']} "
            f"| {r['wins']}/{r['draws']}/{r['losses']} | {r['score']:.3f} "
            f"| [{r['ci_lo']:.3f}, {r['ci_hi']:.3f}] | {r['elo']:+.0f} "
            f"| {r['median_rounds']} | {term} | {'**YES**' if r['balanced'] else 'no'} |")
    return "\n".join(lines) + "\n"


def csv_report(rows: List[Dict]) -> str:
    cols = ["label", "point_id", "n", "wins", "draws", "losses", "score",
            "ci_lo", "ci_hi", "elo", "draw_rate", "median_rounds", "balanced"]
    out = [",".join(cols)]
    for r in rows:
        out.append(",".join(str(r[c]) for c in cols))
    return "\n".join(out) + "\n"


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results_dir")
    ap.add_argument("--md", default=None, help="write markdown report here")
    ap.add_argument("--csv", default=None, help="write csv here")
    args = ap.parse_args(argv)
    rows = summarize(load_records(args.results_dir))
    md = markdown_report(rows)
    if args.md:
        with open(args.md, "w") as f:
            f.write(md)
    if args.csv:
        with open(args.csv, "w") as f:
            f.write(csv_report(rows))
    sys.stdout.write(md)


if __name__ == "__main__":
    main()

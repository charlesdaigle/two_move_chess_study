"""Campaign queue: the adaptive compute policy (strategy.md) as code.

The queue file (experiments/queue/campaigns.json) is the fleet's work order,
versioned in git. Two commands:

  run        node-side: play this node's shard slice of the active campaign.
             Resumable; exits 0 when the slice is complete (or not involved).
  reconcile  controller-side (coralreef agent): when the active campaign's
             games are all on disk, record per-point verdicts, apply the
             escalation policy (double games while ambiguous, lift nodes,
             certify, strength-gate, ladder-bisect), append follow-up
             campaigns, and promote the next pending campaign.

Escalation reuses games: tiers T0->T1a->T1b share a node budget, so their
point_ids match and run_point resumes on top of the earlier tier's records.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import json
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .analysis import load_records, wilson_ci
from .arena import PointSpec, run_point
from .rules import BLACK, WHITE, Ruleset

# tier -> (games, nodes, shard_total). Games at equal nodes accumulate.
TIERS: Dict[str, Tuple[int, int, int]] = {
    "T0": (32, 3000, 4),
    "T1a": (64, 3000, 4),
    "T1b": (128, 3000, 4),
    "T2": (256, 12000, 4),
    "T3": (512, 12000, 4),
    "T4": (128, 24000, 4),
}
NEXT_TIER = {"T0": "T1a", "T1a": "T1b", "T1b": "T2", "T2": "T3"}
BAND = (0.40, 0.60)
CENTER = (0.45, 0.55)
DRIFT_LIMIT = 0.10

# ET-regime ladder ordered by expected double-mover strength (pilot-informed);
# bisection spawns screens for rungs strictly between an opposite-decided pair.
ET_LADDER = [
    "no_q_rr", "knights_pawns", "bishops_pawns", "k_r_pawns", "k_n_pawns",
    "k_b_pawns", "k_n_pawns7", "k_pawns8", "k_pawns7", "k_pawns6", "k_pawns5",
    "monster4", "k_pawns3",
]


# --- queue file ---------------------------------------------------------------

def load_queue(path: str) -> Dict:
    with open(path) as f:
        return json.load(f)


def save_queue(path: str, q: Dict) -> None:
    q["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(path, "w") as f:
        json.dump(q, f, indent=1)
        f.write("\n")


def point_ruleset(pt: Dict) -> Ruleset:
    return Ruleset(
        material=pt["material"],
        check_regime=pt.get("regime", "ET"),
        nc2=pt.get("nc2", False),
        dp2=pt.get("dp2", False),
        k=pt.get("k", 1),
        double_color=WHITE,
        first_player=WHITE if pt.get("first", "W") == "W" else BLACK,
    )


def point_spec(camp: Dict, pt: Dict) -> PointSpec:
    return PointSpec(
        ruleset=point_ruleset(pt),
        games=camp["games"],
        nodes=camp["nodes"],
        alternate_first=pt.get("alternate_first", True),
        label=point_label(camp, pt),
    )


def point_label(camp: Dict, pt: Dict) -> str:
    """Stable across tiers at equal nodes so shard files resume."""
    rs = point_ruleset(pt)
    mods = "".join(["-nc2" if rs.nc2 else "", "-dp2" if rs.dp2 else "",
                    f"-k{rs.k}" if rs.k != 1 else "",
                    "-firstB" if rs.first_player == BLACK else ""])
    alt = "" if pt.get("alternate_first", True) else "-noalt"
    return f"{rs.material}-{rs.check_regime}{mods}{alt}-n{camp['nodes']}"


def point_sig(pt: Dict) -> str:
    """Identity of a point independent of tier (for dedup and T4 lookup)."""
    return json.dumps({k: pt.get(k) for k in
                       ("material", "regime", "nc2", "dp2", "k", "first",
                        "alternate_first")}, sort_keys=True)


# --- run (node side) -----------------------------------------------------------

def cmd_run(args) -> int:
    q = load_queue(args.file)
    active = [c for c in q["campaigns"] if c["status"] == "active"]
    if not active:
        print("no active campaign; nothing to do")
        return 0
    camp = active[0]
    if args.slice >= camp["shard_total"]:
        print(f"slice {args.slice} not used by {camp['id']} "
              f"(shard_total={camp['shard_total']})")
        return 0
    shard = f"{args.slice}/{camp['shard_total']}"
    for pt in camp["points"]:
        spec = point_spec(camp, pt)
        out_path = f"{args.out.rstrip('/')}/{spec.label}.s{args.slice}-{camp['shard_total']}.jsonl"
        run_point(spec, out_path, workers=args.workers, shard=shard)
    print(f"campaign {camp['id']} slice {shard}: complete")
    return 0


# --- reconcile (controller side) ------------------------------------------------

def _point_stats(records_by_pid: Dict[str, List[Dict]], spec: PointSpec):
    recs = [r for r in records_by_pid.get(spec.point_id, ())
            if r.get("double_score") is not None]
    # distinct indices only (shards can overlap after re-slicing)
    seen, scores = set(), []
    for r in recs:
        if r["game_index"] not in seen:
            seen.add(r["game_index"])
            scores.append(r["double_score"])
    n = len(scores)
    s = sum(scores)
    lo, hi = wilson_ci(s, n) if n else (0.0, 1.0)
    return n, (s / n if n else 0.5), lo, hi


def classify(score: float, lo: float, hi: float) -> str:
    if hi < BAND[0]:
        return "decided_single"     # single-mover wins this ruleset
    if lo > BAND[1]:
        return "decided_double"
    if lo >= BAND[0] and hi <= BAND[1] and CENTER[0] <= score <= CENTER[1]:
        return "certifiable"
    return "ambiguous"


def _queued_sigs(q: Dict) -> set:
    return {point_sig(pt) for c in q["campaigns"] for pt in c["points"]}


def _new_campaign(q: Dict, tier: str, points: List[Dict], note: str) -> Dict:
    games, nodes, shard_total = TIERS[tier]
    seq = sum(1 for c in q["campaigns"]) + 1
    camp = {"id": f"{tier.lower()}-{seq:03d}", "tier": tier, "games": games,
            "nodes": nodes, "shard_total": shard_total, "status": "pending",
            "note": note, "points": points, "verdicts": {}}
    q["campaigns"].append(camp)
    return camp


def _bisect_candidates(q: Dict, verdict_by_sig: Dict[str, str]) -> List[Dict]:
    """Spawn screens between opposite-decided adjacent plain-ET ladder rungs."""
    def plain(mat):  # the canonical plain-ET point for a rung
        return {"material": mat, "regime": "ET"}
    decided = {}
    for i, mat in enumerate(ET_LADDER):
        v = verdict_by_sig.get(point_sig(plain(mat)))
        if v in ("decided_single", "decided_double"):
            decided[i] = v
    new_pts, queued = [], _queued_sigs(q)
    idxs = sorted(decided)
    for a, b in zip(idxs, idxs[1:]):
        if decided[a] != decided[b]:
            for mid in range(a + 1, b):
                pt = plain(ET_LADDER[mid])
                if point_sig(pt) not in queued:
                    new_pts.append(pt)
                    queued.add(point_sig(pt))
    return new_pts


def cmd_reconcile(args) -> int:
    q = load_queue(args.file)
    records = load_records(args.results)
    by_pid: Dict[str, List[Dict]] = defaultdict(list)
    for r in records:
        by_pid[r.get("point_id", "")].append(r)

    changed = False
    active = [c for c in q["campaigns"] if c["status"] == "active"]

    if active:
        camp = active[0]
        stats = {}
        complete = True
        for pt in camp["points"]:
            spec = point_spec(camp, pt)
            n, score, lo, hi = _point_stats(by_pid, spec)
            stats[spec.ruleset.rid] = (pt, n, score, lo, hi)
            if n < camp["games"]:
                complete = False
        if complete:
            # 1. record verdicts
            escalate, certify, verdict_by_sig = [], [], {}
            for rid, (pt, n, score, lo, hi) in stats.items():
                verdict = classify(score, lo, hi)
                if camp["tier"] == "T4":
                    base = pt.get("baseline_score", 0.5)
                    drift = score - base
                    verdict = ("strength_sensitive" if abs(drift) > DRIFT_LIMIT
                               else "balanced")
                    pt_note = f"drift {drift:+.3f} vs T3 {base:.3f}"
                elif verdict == "certifiable" and camp["tier"] == "T3":
                    certify.append(pt | {"baseline_score": round(score, 4)})
                    pt_note = "to T4 strength gate"
                elif verdict in ("ambiguous", "certifiable") and camp["tier"] in NEXT_TIER:
                    escalate.append(pt)
                    pt_note = f"to {NEXT_TIER[camp['tier']]}"
                elif verdict in ("ambiguous", "certifiable"):
                    verdict = "near_balanced"   # terminal: ran out of ladder
                    pt_note = "terminal"
                else:
                    pt_note = "terminal"
                camp["verdicts"][rid] = {
                    "n": n, "score": round(score, 4),
                    "ci": [round(lo, 4), round(hi, 4)],
                    "verdict": verdict, "note": pt_note,
                }
                verdict_by_sig[point_sig(pt)] = verdict
            camp["status"] = "done"
            changed = True
            print(f"COMPLETED {camp['id']}")
            # 2. follow-ups
            if escalate:
                nxt = NEXT_TIER[camp["tier"]]
                c = _new_campaign(q, nxt, escalate, f"escalated from {camp['id']}")
                print(f"SPAWNED {c['id']} ({len(escalate)} points)")
            if certify:
                c = _new_campaign(q, "T4", certify, f"strength gate from {camp['id']}")
                print(f"SPAWNED {c['id']} ({len(certify)} points)")
            # 3. ladder bisection on all decided plain-ET rungs so far
            for c_ in q["campaigns"]:
                for rid, v in c_.get("verdicts", {}).items():
                    for pt_ in c_["points"]:
                        if point_spec(c_, pt_).ruleset.rid == rid:
                            verdict_by_sig.setdefault(point_sig(pt_), v["verdict"])
            mids = _bisect_candidates(q, verdict_by_sig)
            if mids:
                c = _new_campaign(q, "T0", mids, "ladder bisection")
                print(f"SPAWNED {c['id']} (bisect: "
                      + ", ".join(p["material"] for p in mids) + ")")

    # promote next pending if nothing active
    if not any(c["status"] == "active" for c in q["campaigns"]):
        pending = [c for c in q["campaigns"] if c["status"] == "pending"]
        if pending:
            pending[0]["status"] = "active"
            changed = True
            print(f"ACTIVATED {pending[0]['id']}")

    if changed:
        save_queue(args.file, q)
        print("CHANGED")
    else:
        act = active[0]["id"] if active else "-"
        done = sum(1 for c in q["campaigns"] if c["status"] == "done")
        print(f"UNCHANGED active={act} done={done}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--file", required=True)
    p_run.add_argument("--out", required=True)
    p_run.add_argument("--workers", type=int, default=1)
    p_run.add_argument("--slice", type=int, required=True)
    p_rec = sub.add_parser("reconcile")
    p_rec.add_argument("--file", required=True)
    p_rec.add_argument("--results", required=True)
    args = ap.parse_args(argv)
    return cmd_run(args) if args.cmd == "run" else cmd_reconcile(args)


if __name__ == "__main__":
    sys.exit(main())

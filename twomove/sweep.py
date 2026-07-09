"""Sweep stages (plan.md) and CLI.

Examples:
    python -m twomove.sweep --stage s0 --out experiments/results/gates
    python -m twomove.sweep --stage s1 --games 60 --nodes 3000 --out .../pilot
    python -m twomove.sweep --stage s2 --games 100 --nodes 3000 --out .../pilot
    python -m twomove.sweep --stage s2b --materials k_pawns6,monster4 --regimes KC \
        --games 300 --nodes 12000 --out .../confirm --shard 0/3
    python -m twomove.sweep --stage s3 --materials no_q_rr,knights_pawns --regimes ET \
        --games 100 --out .../dampers
Then:
    python -m twomove.analysis <out_dir> --md <out_dir>/REPORT.md
"""

from __future__ import annotations

import argparse
import dataclasses
import re
from typing import List

from .arena import PointSpec, run_point
from .rules import BLACK, ET, IL, KC, LADDER, WHITE, Ruleset

PILOT_LADDER = [m for m in LADDER if m != "full"]


def _label(stage: str, rs: Ruleset, extra: str = "") -> str:
    lab = f"{stage}-{rs.material}-{rs.check_regime}"
    mods = "".join([
        "-nc2" if rs.nc2 else "", "-dp2" if rs.dp2 else "",
        f"-k{rs.k}" if rs.k != 1 else "",
        "" if rs.first_player == WHITE else "-firstB",
    ])
    return lab + mods + (f"-{extra}" if extra else "")


def stage_points(args) -> List[PointSpec]:
    g, n = args.games, args.nodes
    regimes = args.regimes.split(",") if args.regimes else None
    mats = args.materials.split(",") if args.materials else None
    pts: List[PointSpec] = []

    if args.stage == "s0":
        # Gate A: search double-mover vs RANDOM single-mover (expect ~1.0) and the
        # reverse handicap sanity (random double vs search single, expect ~0.0).
        for mat, reg in [("no_q_rr", ET), ("monster4", KC), ("k_pawns6", ET)]:
            rs = Ruleset(material=mat, check_regime=reg)
            pts.append(PointSpec(rs, g, n, engine="search", engine_single="random",
                                 label=_label("s0vsrandS", rs)))
            pts.append(PointSpec(rs, g, n, engine="random", engine_single="search",
                                 label=_label("s0vsrandD", rs)))
        # Gate B: budget scaling — 2x nodes on one side must outscore the same
        # ruleset with 2x on the other side.
        for mat, reg in [("no_q_rr", ET), ("k_pawns6", KC)]:
            rs = Ruleset(material=mat, check_regime=reg)
            pts.append(PointSpec(rs, g, 2 * n, nodes_single=n,
                                 label=_label("s0scaleD", rs)))
            pts.append(PointSpec(rs, g, n, nodes_single=2 * n,
                                 label=_label("s0scaleS", rs)))
        return pts

    if args.stage == "s1":  # H1: symmetric material blowout check
        for reg in regimes or (KC, ET, IL):
            rs = Ruleset(material="full", check_regime=reg)
            pts.append(PointSpec(rs, g, n, label=_label("s1", rs)))
        return pts

    if args.stage == "s2":  # H2/H3: material ladder
        for reg in regimes or (KC, ET):
            for mat in mats or PILOT_LADDER:
                rs = Ruleset(material=mat, check_regime=reg)
                pts.append(PointSpec(rs, g, n, label=_label("s2", rs)))
        return pts

    if args.stage == "s2b":  # bisection refinement: explicit materials required
        assert mats and regimes, "--materials and --regimes required for s2b"
        for reg in regimes:
            for mat in mats:
                rs = Ruleset(material=mat, check_regime=reg)
                pts.append(PointSpec(rs, g, n, label=_label("s2b", rs)))
        return pts

    if args.stage == "s3":  # H4: damper stacking near the crossing
        assert mats, "--materials required for s3"
        for reg in regimes or (ET,):
            for mat in mats:
                for nc2, dp2 in [(True, False), (False, True), (True, True)]:
                    rs = Ruleset(material=mat, check_regime=reg, nc2=nc2, dp2=dp2)
                    pts.append(PointSpec(rs, g, n, label=_label("s3", rs)))
        return pts

    if args.stage == "s4":  # doubling period
        assert mats, "--materials required for s4"
        for reg in regimes or (ET,):
            for mat in mats:
                rs = Ruleset(material=mat, check_regime=reg, k=2)
                pts.append(PointSpec(rs, g, n, label=_label("s4", rs)))
        return pts

    if args.stage == "s5":  # H6: turn-order value at near-balanced points
        assert mats, "--materials required for s5"
        for reg in regimes or (ET,):
            for mat in mats:
                for first in (WHITE, BLACK):  # double_color is always WHITE
                    rs = Ruleset(material=mat, check_regime=reg, first_player=first)
                    pts.append(PointSpec(rs, g, n, alternate_first=False,
                                         label=_label("s5", rs)))
        return pts

    raise SystemExit(f"unknown stage {args.stage!r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True,
                    help="s0 gates | s1 blowout | s2 ladder | s2b bisect | s3 dampers"
                         " | s4 period | s5 turn order")
    ap.add_argument("--games", type=int, default=100)
    ap.add_argument("--nodes", type=int, default=3000)
    ap.add_argument("--materials", default="", help="comma list (see rules.LADDER)")
    ap.add_argument("--regimes", default="", help="comma list of KC,ET,IL")
    ap.add_argument("--out", required=True, help="results directory (JSONL per point)")
    ap.add_argument("--workers", type=int, default=0, help="0 = all cores")
    ap.add_argument("--shard", default=None, help="i/N: play games with index%%N==i")
    ap.add_argument("--dry-run", action="store_true", help="list points and exit")
    args = ap.parse_args(argv)

    points = stage_points(args)
    print(f"{len(points)} points, {sum(p.games for p in points)} games max")
    for p in points:
        print(f"  {p.label}: {p.point_id} x{p.games}")
    if args.dry_run:
        return
    shard_tag = f".s{args.shard.replace('/', '-')}" if args.shard else ""
    for p in points:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", p.label or p.point_id)
        out_path = f"{args.out.rstrip('/')}/{safe}{shard_tag}.jsonl"
        print(f"== {p.label} -> {out_path}")
        run_point(p, out_path, workers=args.workers, shard=args.shard)


if __name__ == "__main__":
    main()

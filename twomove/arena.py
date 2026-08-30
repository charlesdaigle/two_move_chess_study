"""Self-play arena: run matches for a sweep point, write JSONL game records.

Distribution model (plan.md): games of a point are indexed 0..N-1; seeds derive from
the index, so any subset of indices can run anywhere (e.g. `--shard 1/3` on a Pi) and
the JSONL files merge by concatenation. Records are self-describing.
"""

from __future__ import annotations

import dataclasses
import json
import multiprocessing as mp
import os
import time
import zlib
from typing import Dict, List, Optional

from .engine import ENGINES
from .rules import BLACK, WHITE, GameState, Ruleset


@dataclasses.dataclass(frozen=True)
class PointSpec:
    """One sweep point: a ruleset played for `games` games.

    Engines/budgets are per role so validation gates can pit asymmetric players
    (search vs random, 2x vs 1x nodes). Normal sweep points keep them identical.
    """
    ruleset: Ruleset
    games: int
    nodes: int                       # double-mover's budget
    engine: str = "search"           # double-mover's engine
    nodes_single: int = 0            # 0 -> same as nodes
    engine_single: str = ""          # "" -> same as engine
    alternate_first: bool = True     # game i odd -> first_player flipped
    label: str = ""

    @property
    def point_id(self) -> str:
        ns = self.nodes_single or self.nodes
        es = self.engine_single or self.engine
        pid = f"{self.ruleset.rid}|n={self.nodes}|e={self.engine}"
        if (ns, es) != (self.nodes, self.engine):
            pid += f"|ns={ns}|es={es}"
        return pid


def game_ruleset(spec: PointSpec, game_index: int) -> Ruleset:
    rs = spec.ruleset
    if spec.alternate_first and game_index % 2 == 1:
        rs = dataclasses.replace(rs, first_player=not rs.first_player)
    return rs


def play_game(spec: PointSpec, game_index: int, max_halfmoves: int = 1200) -> Dict:
    rs = game_ruleset(spec, game_index)
    # deterministic across processes and machines (Python's hash() is salted)
    seed = zlib.crc32(f"{spec.point_id}#{game_index}".encode()) & 0x7FFFFFFF
    single = not rs.double_color
    engines = {
        rs.double_color: ENGINES[spec.engine](nodes=spec.nodes, seed=seed * 2 + 1),
        single: ENGINES[spec.engine_single or spec.engine](
            nodes=spec.nodes_single or spec.nodes, seed=seed * 2 + 2),
    }
    state = GameState(rs)
    moves: List[str] = []
    t0 = time.time()
    while state.outcome() is None and len(moves) < max_halfmoves:
        move = engines[state.mover].choose(state)
        moves.append(move.uci())
        state.push(move)
    out = state.outcome()
    if out is None:                      # hit the half-move guard: score as cap-draw
        winner, reason = None, "cap"
    else:
        winner, reason = out.winner, out.reason
    if winner is None:
        score = 0.5
    else:
        score = 1.0 if winner == rs.double_color else 0.0
    return {
        "point_id": spec.point_id,
        "label": spec.label,
        "ruleset": rs.rid,
        "game_index": game_index,
        "seed": seed,
        "nodes": spec.nodes,
        "engine": spec.engine,
        "double_score": score,
        "reason": reason,
        "n_halfmoves": len(moves),
        "n_rounds": state.turns_played // 2,
        "elapsed_s": round(time.time() - t0, 2),
        "moves": " ".join(moves),
    }


def _worker(args):
    spec, idx = args
    try:
        return play_game(spec, idx)
    except Exception as e:  # never lose a whole shard to one game
        return {"point_id": spec.point_id, "game_index": idx, "error": repr(e),
                "double_score": None, "reason": "error", "ruleset": spec.ruleset.rid,
                "label": spec.label}


def existing_indices(path: str, point_id: str) -> set:
    done = set()
    if not os.path.exists(path):
        return done
    with open(path) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("point_id") == point_id and rec.get("reason") != "error":
                done.add(rec["game_index"])
    return done


def run_point(spec: PointSpec, out_path: str, workers: int = 0,
              shard: Optional[str] = None, quiet: bool = False) -> None:
    """Play all (remaining) games of a point, appending records to out_path."""
    indices = list(range(spec.games))
    if shard:
        i, n = (int(x) for x in shard.split("/"))
        indices = [g for g in indices if g % n == i]
    done = existing_indices(out_path, spec.point_id)
    todo = [g for g in indices if g not in done]
    if not todo:
        return
    workers = workers or max(1, mp.cpu_count() - 0)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    jobs = [(spec, g) for g in todo]
    t0 = time.time()
    with open(out_path, "a") as f:
        if workers == 1:
            it = map(_worker, jobs)
            for k, rec in enumerate(it, 1):
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if not quiet:
                    _progress(spec, k, len(jobs), t0)
        else:
            with mp.Pool(workers) as pool:
                for k, rec in enumerate(pool.imap_unordered(_worker, jobs), 1):
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    if not quiet:
                        _progress(spec, k, len(jobs), t0)


def _progress(spec: PointSpec, k: int, n: int, t0: float) -> None:
    rate = k / max(time.time() - t0, 1e-9)
    eta = (n - k) / max(rate, 1e-9)
    print(f"  [{spec.label or spec.point_id}] {k}/{n} games "
          f"({rate*3600:.0f}/h, eta {eta/60:.0f}m)", flush=True)

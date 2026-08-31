# Perturbation study — evolve standard chess one knob at a time

**Started 2026-08-31.** Motivation: the pilot's material ladder hunts *down* from
K+pawns and lands on sharp mating-race games. At 12k nodes both pilot candidates
failed certification in opposite directions:

| rung | pilot 3k | strong 12k | verdict |
|---|---|---|---|
| `k_n_pawns` K+N+8P | 0.562 | 0.662 | double-mover favored |
| `k_pawns8` K+8P | 0.531 | 0.372 | single-mover favored |

One knight swings the score 0.29 — there is no clean material rung in the band.
So instead: **start from standard chess** (full army, two-move axiom — a known
1.000 blowout) and perturb ONE parameter at a time, then promising PAIRS, and see
what lands near 50%. The theory (research.md §2.1) says material can't balance an
unbounded tempo annuity; the knobs that *can* are the ones that attack the annuity
itself — dampers (`nc2`, `dp2`), doubling period (`k`), turn order.

## What runs (`run.sh`)

100 points, N=384 (Wilson 95% CI half-width ~0.05), 8000 nodes/half-move (strong
enough that verdicts don't flip vs 12k; the pilot showed 3k does). Ordered
most-informative-first so an 18h timeout loses the least.

| batch | stage | what it perturbs |
|---|---|---|
| `B_s3_trim_damper` | s3 | {no_q, no_r, no_rr, no_nn, no_bb, no_q_r, no_q_rr} x {nc2, dp2, both} x {ET, IL} — trim + a damper (2 knobs) |
| `B_s4_trim_k2` | s4 | those trims with `k=2` |
| `A_s2_material` | s2 | one piece removed from the full army, no damper (1 knob) — new schemes in `rules.py`: `full_p7/p6`, `no_n/b/r`, `no_nn/bb/rr`, `no_q_n/b/nn/bb` |
| `A_s3_full_damper` | s3 | standard army + exactly one damper |
| `A_s4_full_k2` | s4 | standard army + `k=2` |
| `B_s5_trim_order` / `A_s5_full_order` | s5 | turn-order flip (single-mover moves first) |
| `A_s1_refs` | s1 | full-material blowout references (ET, IL) |

KC (king-capture) is deliberately excluded — the pilot proved it is unbalanceable
by material, and it is not a target.

## Reading results

`REPORT.md` here is regenerated and committed after every sub-batch (sorted by
distance from 0.5; `balanced` flag = Wilson CI in [0.40,0.60] and score in
[0.45,0.55]). Raw JSONL alongside it. `driver.log` has timings. A `DONE` file
appears when all batches finish.

Next session: take every point whose CI touches [0.40, 0.60] and re-run it at
N>=768 / 12k nodes to certify, then feed the survivors to the MAP-Elites explorer
as seeds (they are the "recognizable chess that balances" region).

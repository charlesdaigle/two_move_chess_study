# Adaptive Compute Strategy: screen cheap, escalate on strikes

**Supersedes** the static stage queue in DISTRIBUTED.md as the scheduling policy
(the stages remain the vocabulary; this doc decides *what runs when and how big*).

## Principle

Most sweep points are decided by ~32 games — the pilot proved it: 17 of 23 points
landed ≥0.78 or ≤0.16, where more games buy nothing. Information concentrates at
points whose confidence interval touches the balance band. So: **screen every new
point at minimum size, escalate by doubling only while the point stays ambiguous,
and shard fleet-wide only at the top of the ladder.** Total compute per point is
geometric, so the expensive tiers are reached only by the few points that matter —
the "binary search" is over sample size and over the material ladder simultaneously.

## The escalation ladder

| Tier | Games | Nodes | Runs on | Purpose |
|---|---|---|---|---|
| T0 screen | 32 | 3k | coralreef alone | triage a new point (~2–5 Pi4-hours) |
| T1 double | 64 → 128 | 3k | coralreef alone | separate CI from the band |
| T2 strike | 256 | 12k | **all nodes, sharded** | strength-stable estimate |
| T3 certify | 512 | 12k | all nodes, sharded | τ=0.05 certification (CI ⊆ [0.45,0.55]-ish) |
| T4 gate | 128 | 24k | all nodes, sharded | strength-drift check on certified points |

**Escalation rule** (mechanical, per point, after each tier completes):
- **Decided** — Wilson 95% CI entirely outside [0.40, 0.60]: STOP, record verdict.
- **Ambiguous** — CI overlaps the band: escalate one tier.
- **Certified** — at T3, CI ⊆ [0.40, 0.60] with score in [0.45, 0.55]: run T4 once.
  Drift >0.10 toward the double-mover at T4 ⇒ mark *strength-sensitive* (a finding,
  per research.md §5), else **declare balanced** — a terminal positive result.
- Node escalation (3k→12k between T1 and T2) exists because weak play flatters the
  double-mover; a point that survives T1 must re-prove itself at 4× strength.

**Strike definitions** (what earns T2+, besides ambiguity):
1. **Crossing bracket**: adjacent ladder rungs decided on opposite sides of 0.5 →
   run the midpoint rung(s) at T0 (ladder bisection, below).
2. **Surprise**: a decided result that contradicts a registered hypothesis or an
   adjacent tier's result (e.g. the pilot's knights≫bishops non-monotonicity) →
   replicate once at the next tier before believing it.
3. **Hypothesis leverage**: a point whose outcome chooses between H-verdicts
   (currently: KC-sensitivity — monster4/k_pawns3 under KC at 12k nodes — tests
   whether "KC can't be balanced by material" survives stronger defense).

## Ladder bisection targets (new interpolation rungs)

The pilot bracket is knights_pawns (0.97) ≻ … ≻ k_n_pawns (0.56) ≻ k_pawns8
(0.53) ≻ … ≻ k_pawns6 (0.16). New schemes in `rules.py` populate the gaps, pawns
thinning flank-inward to stay "logical":

| Scheme | Army | ~pawns | Probes |
|---|---|---|---|
| `k_r_pawns` | K+R(a1)+8P | 13 | rook² potency at the crossing |
| `k_b_pawns` | K+B(c1)+8P | 11.25 | N-vs-B potency, paired with `k_n_pawns` |
| `k_n_pawns7` | K+N(b1)+7P (b–h) | 10 | between k_n_pawns and k_pawns8 |
| `k_pawns7` | K+7P (b–h) | 7 | between k_pawns8 and k_pawns6 |
| `k_pawns5` | K+5P (c–g) | 5 | between k_pawns6 and monster4 |

## Beginning phase (incremental gains): the T0 screening frontier

Everything below is T0 (32 games @ 3k) on coralreef — cheap survey first, ~15
points ≈ 2–4 Pi4-days total, before any large confirmation burn:

1. New rungs: `k_r_pawns`, `k_b_pawns`, `k_n_pawns7`, `k_pawns7` under ET.
2. Damper stack (S3): {nc2, dp2, both} × {knights_pawns, bishops_pawns, no_q_rr}
   under ET — the "can bigger armies balance?" question.
3. Turn order (S5): first_player=B at k_n_pawns and k_pawns8.
4. Doubling period (S4): k=2 at no_q_rr and knights_pawns.

Then the escalation rule takes over: ambiguous/striking points climb tiers and get
sharded to node1/node2; decided points stop at 32 games. The prior static plan
("run S2b at 300 games first") is *retired* — certification burn is earned, not
scheduled.

## Queue mechanics (automation-ready)

Campaigns live in `experiments/queue/campaigns.json`: an ordered list of
`{id, points (sweep CLI args), games, nodes, status: pending|active|done|verdict}`.
The escalation rule is deterministic, so it can run as code on coralreef
(auto-append follow-up campaigns when a tier completes) or be curated by Claude
editing the file from chat — an open deployment decision. Either way the repo is
the message bus: campaign specs flow down in commits; JSONL results flow back up.

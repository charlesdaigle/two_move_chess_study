# Implementation Plan: Balancing Two-Move Chess

**Branch**: `claude/two-move-chess-balance-mku5j2` | **Date**: 2026-07-09
**Spec**: `spec.md` | **Research**: `research.md`

## Summary
Build (1) a configurable two-move-chess rules kernel, (2) a variant-aware alpha-beta
engine, (3) a self-play arena, and (4) a staged **parameter sweep** with statistical
analysis, to locate balanced rulesets predicted by `research.md`.

## Technical Context
**Language**: Python 3.11 (pure-Python `python-chess` 1.11 vendored for board
primitives/legality; our own turn-structure layer on top).
**Why not an existing engine**: research.md §5 — no strong engine supports multi-move
turns; engine strength shifts the balance point, so both sides must run the *same*
search at fixed node budgets.
**Testing**: pytest-style unit tests (runnable with plain `python -m tests.run`),
full-game legality audits.
**Performance target**: ≥5k search nodes/sec/core → a 3k-nodes-per-half-move game
(~120 half-moves) in ≤90s; 4 cores → pilot stages of ~100–400 games feasible per run.
**Constraints**: results must be reproducible (seeded), resumable (append-only JSONL),
and honest about engine-strength sensitivity (budget-scaling gate).

## Project Structure

```
specs/001-two-move-balance/   # spec.md, research.md, plan.md, tasks.md
twomove/
    rules.py       # Ruleset dataclass, material schemes, GameState (turn schedule,
                   # legality per check regime, terminations, repetition)
    engine.py      # alpha-beta over half-move tree, TT, qsearch, node budgets,
                   # root softmax diversification; Random + Greedy baselines
    arena.py       # play_game, match runner (multiprocessing), JSONL records
    analysis.py    # Wilson CI, Elo-equivalent, per-ruleset + sweep reports (md/csv)
    sweep.py       # named stages (validate/h1/h2-ladder/h3/h4/h6), bisection helper
tests/
    test_rules.py  # edge cases from spec.md; legality audits vs python-chess
    test_engine.py # tactics the engine must see; scaling + vs-random gates
experiments/
    configs/       # stage specs (JSON)
    results/       # JSONL game records + generated reports (committed for pilots)
```

## Engine Design (core difficulty, per research.md §5)

- **Game tree**: nodes are half-moves. `GameState` exposes `mover()` (whose half-move),
  `legal_halfmoves()`, `push/pop`. Alpha-beta chooses max/min by *node owner*;
  consecutive same-owner plies do not alternate sign. TT key = (zobrist, half-index,
  owner, schedule phase).
- **Budgets**: fixed nodes per half-move decision (default 3000 pilot / 12000
  confirm). Both sides identical. Iterative deepening; depth measured in half-moves.
- **Quiescence**: capture-only (plus king-capture threats under KC), schedule-aware.
- **Eval**: material + piece-square tables + small mobility/tempo term. Orthodox
  weights first (upgrade lever: king-threat exposure + passed-pawn urgency terms).
- **KC regime**: pseudo-legal movegen, king capture = terminal win — faster search.
  ET/IL regimes: python-chess legality per half-move; ET grants turn-ending first-move
  checks; IL filters them out.

## Sweep Design (the parameter sweep the study centers on)

Stages map 1:1 to research.md §3 hypotheses. Each stage = config JSON + one command.

| Stage | Question | Grid | Games/pt |
|---|---|---|---|
| S0 gates | engine sane? | vs-random, 2×-vs-1× budget, on 3 rulesets | 40–100 |
| S1 blowout (H1) | is `full` hopeless in every regime? | `full` × {KC,ET,IL} | 60 |
| S2 ladder (H2,H3) | where does 50% cross? | material ladder (§4) × {KC,ET} | 100 |
| S2b bisect | refine crossing | bisection between bracketing rungs | 300+ |
| S3 dampers (H4) | how much do NC2/DP2 buy? | {NC2,DP2,both} × 3 rungs near crossing | 100 |
| S4 period | k as fine knob | k∈{1,2} at crossing rungs | 100 |
| S5 order (H6) | first-move value | swap `first_player` at near-balanced pts | 200 |

Every point is played with turn order alternating game-by-game unless the stage sweeps
it explicitly; seeds = game index; root-softmax opening diversification for the first
8 full turns.

**Decision rule**: a rung is *balanced* if Wilson 95% CI for double-mover score ⊆
[0.40, 0.60] and centered within [0.45, 0.55]; *crossing bracket* = adjacent rungs with
CIs on opposite sides of 0.5. Monotonicity check across the ladder before bisecting.

**Budget-sensitivity gate**: any rung declared balanced is replayed at 4× nodes with
N=100; if the score moves by more than 10 points toward the double-mover... report as
"balance unstable under strength" (research.md §5 predicts weak play flatters the
double-mover — the sign of the drift is itself a finding).

## Distributed long-run mode (home Pi cluster)

Confirmation stages (S2b/S5, N≥300/point) are cheap to parallelize: games are
independent, seeded by game index, and appended to JSONL. We support a zero-coordination
distribution model for the user's Raspberry Pi 4B+ and 2× Pi Zero 2W:

- `--shard i/N` on the sweep/arena CLI: node *i* plays exactly the games whose index
  ≡ i (mod N) — deterministic, no queue or network coordination needed.
- Each node writes `<point>.<shard>.jsonl`; `analysis.py` aggregates a whole results
  directory (any mix of shards), so merging = `rsync`/`scp` the files together.
- Memory guard for the Zero 2Ws (512 MB): TT entry cap (`--tt-mb`), single worker.
- Setup, throughput expectations, and systemd/nohup recipes: `experiments/DISTRIBUTED.md`.
  Rough budget: Pi 4B ≈ hundreds of pilot-budget games/day on 4 workers; the Zeros
  combined add roughly half that at reduced node budget — enough to run S2b-scale
  points continuously in the background while interactive work happens elsewhere.
- Caveat: the cloud session cannot reach the home network; the user launches shards,
  then commits or uploads the JSONL for joint analysis.

## Statistics
Wilson CI on score (draws = ½), Elo-equivalent, termination-reason and game-length
distributions per point; sweep report ranks by |s−0.5| and flags draw rate >60%
(playability) per spec.md. All numbers regenerable from JSONL via `analysis.py`.

## Phases
- **Phase 0** (done): research.md.
- **Phase 1**: rules kernel + tests (spec.md edge cases are the test list).
- **Phase 2**: engine + gates (S0).
- **Phase 3**: arena/sweep/analysis + pilot S1–S2 at pilot budget; commit results.
- **Phase 4**: full-budget confirmation runs, S3–S5, findings write-up
  (`experiments/results/REPORT.md`), iterate rulesets if no balanced point found.

## Risks
- **Python speed** caps engine strength → mitigations: KC pseudo-legal fast path, TT,
  qsearch discipline, node budgets not depth; findings gated by budget-scaling check.
- **Draw/cap pathologies** near balance → cap sweeps + termination-reason reporting.
- **Non-monotone ladder** (piece synergies) → full coarse sweep before bisection.

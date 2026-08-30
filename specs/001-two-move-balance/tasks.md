# Tasks: Balancing Two-Move Chess

**Input**: plan.md, research.md, spec.md on this branch.
Ordering: rules kernel before engine; engine gates before any sweep numbers are
believed; pilot sweep before full-budget confirmation.

## Phase 1: Rules kernel
- [x] T001 Ruleset dataclass + material schemes table (`twomove/rules.py`) —
      parameters exactly per research.md §4.
- [x] T002 GameState: turn schedule (doubling period k, first_player), half-move
      legality per check regime (KC/ET/IL), NC2/DP2 restrictions, terminations
      (king capture, checkmate, stalemate, repetition incl. within-turn state,
      move cap), en-passant "last half-move only" rule.
- [x] T003 [P] Unit tests for every edge case in spec.md §Edge Cases
      (`tests/test_rules.py`).

## Phase 2: Engine
- [x] T004 Alpha-beta over half-move tree with owner-based max/min, TT, iterative
      deepening under node budget, schedule-aware quiescence (`twomove/engine.py`).
- [x] T005 Eval: material + PST + tempo term; Random and Greedy baselines.
- [x] T006 Root softmax diversification (first 8 full turns, seeded).
- [x] T007 Engine gate tests: sees 2-half-move mate/king-capture; ≥99% vs random;
      2× budget > 1× budget (`tests/test_engine.py`, S0 in sweep).

## Phase 3: Arena, sweep, analysis
- [x] T008 play_game + multiprocessing match runner, JSONL game records, resumable
      (`twomove/arena.py`).
- [x] T009 Wilson CI / Elo / termination stats; per-point and sweep markdown+CSV
      reports (`twomove/analysis.py`).
- [x] T010 Sweep stages S0–S5 as configs + CLI (`twomove/sweep.py`,
      `experiments/configs/`).

## Phase 4: Experiments
- [x] T011 Run S0 gates; do not proceed until they pass.
- [x] T012 Pilot S1 (H1 blowout) + S2 ladder at pilot budget; commit JSONL + report.
- [ ] T013 S2b confirmation at 12000 nodes on the ET crossing bracket
      (`k_n_pawns`, `k_pawns8`) — Pi cluster queue item 1 (DISTRIBUTED.md).
- [ ] T014 S3 damper sweep (NC2/DP2) at `knights_pawns`/`bishops_pawns`/`no_q_rr`
      under ET; S4 period sweep; S5 turn order at the certified rung.
- [ ] T015 Budget-sensitivity gate: KC bottom rungs + ET crossing at 4× nodes.
- [x] T016 pilot findings write-up `experiments/results/REPORT.md`; research.md
      hypothesis verdicts updated (H1✓ H2✗ H3✓dir H5✓ P3✓; H4/H6 pending).
      Candidate balanced rulesets: **ET + K+N+8P (0.562)**, **ET + K+8P (0.531)**.

## Backlog / upgrade levers
- [ ] T017 Eval upgrade: single-mover king threat-exposure term, double-mover
      passed-pawn urgency (research.md §5.4).
- [ ] T018 Faster kernel (bitboard turn layer or Rust port) if Python nodes/sec
      caps the strength gate.
- [ ] T019 Positional handicaps stage (pawns on 3rd rank, pre-developed
      single-mover) if material+dampers can't reach τ=0.05.

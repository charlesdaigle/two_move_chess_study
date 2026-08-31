# twomove Rust engine

Replaces `twomove/engine.py` + the `python-chess` half of `twomove/rules.py` for
all real runs. Python stays only as the differential-test oracle and is dropped
once the port is trusted. Rationale and phasing: the project build plan
(`../PLAN.md` pointer / the published plan artifact).

## Why Rust, why now
- `python-chess` hard-codes 8x8 orthodox pieces. Boards up to 12x12 and Betza
  fairy pieces need a new movegen regardless of language.
- The expanded search space (board size x army x fairy pieces x dampers x turn
  order) needs throughput the Python alpha-beta can't give on the Pi fleet.

## Layout
```
engine/
  core/   twomove-core  — geometry, piece, board, rules, movegen, turn, eval, search, perft
  cli/    twomove       — line-protocol binary that twomove/arena.py drives
```

## Port discipline (do not skip)
1. Orthodox pseudo-legal movegen on 8x8; `perft` to depth 6 on startpos +
   Kiwipete + >=3 more.
2. Differential test vs `python-chess` on 10k random positions, regimes off.
3. Port turn schedule + ET/IL/KC legality; Marseillais perft to depth 4 counted
   two independent ways (this generator + instrumented `twomove/rules.py`).
4. Port `SearchEngine` faithfully — node budget not depth, owner-based min/max,
   schedule-aware quiescence, seeded root softmax. Match the Python RNG stream so
   recorded games replay.
5. **Only then**: reproduce the Python engine's move choices across the committed
   pilot corpus (`experiments/results/pilot/*.jsonl`). That is T2's "done when".
6. After the diff test passes, add king-safety + mobility eval terms as
   separately-benchmarked changes (research.md section 5).

## Build
```
cd engine && cargo test && cargo build --release
# cross-compile for the Pis (aarch64) later: rustup target add aarch64-unknown-linux-gnu
```

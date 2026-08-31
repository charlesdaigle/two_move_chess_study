# Status — 2026-08-31

Plan (course-corrected): https://claude.ai/code/artifact/f658ad76-d54f-403c-af0d-6e0fb4b62b56

## Fleet

| host | addr | hw | state |
|---|---|---|---|
| ocean | (this box) | i7-13700F (24t), 16 GB, RTX 3060 Ti 8 GB | **running the perturbation study** |
| node0 | 10.0.1.100 | Pi 4B, 8 GB, 4 cores | idle / spare |
| node1/2 | 10.0.1.101/2 | Pi Zero 2 W, 512 MB | idle |

Ocean runs sweeps ~22x faster than node0 (measured: 2270 games/h vs 104/h at
12k nodes) — long compute belongs on ocean, not the Pis.

## GPU — verified for compute
`nvidia-smi`: driver 595.84, CUDA 13.2, RTX 3060 Ti, 7.66 GiB usable, idle.
PyTorch cu128 in `~/gpu-check` venv: `cuda available: True`, cc 8.6 (Ampere),
bf16 supported, ~8.4 TFLOP/s fp32 on a naive matmul. Ready for Phase 08 / the
supervisor model. (Nothing uses the GPU yet.)

## Certification — CLOSED, both pilot candidates falsified

| rung | pilot (3k, N=32) | strong (12k) | verdict |
|---|---|---|---|
| `k_n_pawns` K+N+8P | 0.562 | **0.662** (N=463, CI [0.618, 0.704]) | double-mover favored |
| `k_pawns8` K+8P | 0.531 | **0.380** (N=465, CI [0.337, 0.424]) | single-mover favored |

One knight swings the score 0.28 at strength — no clean material rung lands in
the [0.45,0.55] band. Material tuning alone can't produce a balanced game.
Results in `experiments/results/ocean/`.

## RUNNING — perturbation study (ocean, branch `perturbation-study`)

`experiments/perturbation/run.sh`, launched via `nohup timeout 18h ...`.
Driver PID recorded in `experiments/results/perturbation/driver.log` (first line
region). 100 points, N=384, 8000 nodes, 20 workers. Est. 13-17h; hard cap 18h.

Evolve standard chess one knob at a time: dampers (`nc2`/`dp2`), doubling period
(`k=2`), turn-order flip, single piece removals (new `rules.py` schemes:
`full_p7/p6`, `no_n/b/r`, `no_nn/bb/rr`, `no_q_n/b/nn/bb`), then promising pairs.
Design + rationale: `experiments/perturbation/README.md`.

- Live report: `experiments/results/perturbation/REPORT.md` (regenerated +
  committed + pushed after every sub-batch).
- `experiments/results/perturbation/DONE` appears when finished.
- Resume after a crash: `bash experiments/perturbation/run.sh` (skips recorded games).
- Stop: `kill <driver pid>` then `pkill -f 'sweep --stage'` (do NOT
  `pkill -f twomove.sweep` — it matches its own shell).

## Rust engine — branch `rust-engine` (paused during the study)
`engine/` Cargo workspace scaffolded, `cargo test` green, movegen/search stubbed.
Next: orthodox pseudo-legal movegen + perft to depth 6. See `engine/README.md`.

## Env
- ocean venv `.venv` (python-chess 1.11.2, py3.14), 42 tests pass.
- rustup at `~/.cargo/bin` (Rust 1.98). gh logged in (ssh), push works.

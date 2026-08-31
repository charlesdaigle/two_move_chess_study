# Status — 2026-08-30

Course-corrected build plan (published):
https://claude.ai/code/artifact/f658ad76-d54f-403c-af0d-6e0fb4b62b56

## Fleet

| host | addr | hw | role |
|---|---|---|---|
| ocean | (this box) | i7-13700F, 16 GB, RTX 3060 Ti 8 GB | controller, Rust build, analysis; later Postgres + dashboard + finalist training |
| node0 | 10.0.1.100 | Pi 4B, 8 GB, 4 cores, Debian 13 | S2b certification worker |
| node1 | 10.0.1.101 | Pi Zero 2 W, 512 MB, 4 cores | idle (best-effort tier) |
| node2 | 10.0.1.102 | Pi Zero 2 W, 512 MB | idle |

Ocean -> Pi SSH: user `node`, key `~/.ssh/id_ed25519`, all three reachable.
`deploy/ansible/inventory.ini` written for this topology; `ansible pis -m ping` green.
No git on the Pis — code gets there by `rsync` from ocean.

## Track 1 — certification (running on node0)

Launched via `nohup` (no tmux on the Pi), logging to
`experiments/results/incoming/s2b.log`, 4 workers, `nice -n 10`:

```
python -m twomove.sweep --stage s2b --materials k_n_pawns,k_pawns8 \
  --regimes ET --games 512 --nodes 12000 --out experiments/results/incoming
```

Certifies (or moves) the two pilot candidates — `k_n_pawns` (0.562) and
`k_pawns8` (0.531) under ET — at 4x the pilot node budget, N=512 (tau=0.05 needs
N>=~384). Early rate ~100-120 games/h; both points ~overnight. Resumable: re-run
the same command to continue.

Monitor / collect / stop:
```
ssh node@10.0.1.100 'tail -f ~/two_move_chess_study/experiments/results/incoming/s2b.log'
rsync -a node@10.0.1.100:~/two_move_chess_study/experiments/results/incoming/ experiments/results/incoming/
.venv/bin/python -m twomove.analysis experiments/results/incoming
ssh node@10.0.1.100 'pkill -f twomove.sweep'
```

Still pending after this: S3 dampers + S5 turn order + the 4x budget gate
(the plan's Track 1). node1/node2 will get the cheaper S3 screen (3k nodes)
once it's set up — their RAM (~400 MB free) is too tight for the 12k run.

## Track 2 — Rust engine (scaffold on branch `rust-engine`)

`engine/` — Cargo workspace, `cargo test` green (5 pass, 1 ignored).
- `core/`: geometry (parameterized, 12x12 ceiling), piece, board (mailbox),
  rules, and stubbed `movegen` / `turn` / `eval` / `search` / `perft` with
  port notes.
- `cli/`: `twomove` binary, line protocol (`engine/PROTOCOL.md`) — `id`/`ping`
  wired, game commands stubbed.
- Port order and "faithful first" discipline: `engine/README.md`.

Next: implement orthodox pseudo-legal movegen + perft to depth 6.

## Environment notes
- ocean Python is 3.14; project venv at `.venv` (python-chess 1.11.2). 42 tests pass.
- `analysis.py` reproduces the committed pilot REPORT numbers exactly.
- Rust 1.98 via rustup at `~/.cargo/bin`.

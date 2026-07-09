# Running sweep shards on home hardware (Pi 4B+, Pi Zero 2W)

Games are independent and seeded by game index, so distribution needs **no
coordination**: each node plays the slice of game indices `index % N == i` and
appends to its own JSONL file; analysis merges every `*.jsonl` it finds in a
directory. To combine results, just copy the files into one directory.

## Install (once per node)

```bash
sudo apt install -y python3 git
git clone <this repo> && cd two_move_chess_study
pip3 install chess
# If the wheel build fails with "AttributeError: install_layout" (Debian setuptools
# quirk), install from the sdist manually:
#   pip3 download chess --no-deps -d /tmp/pkg && cd /tmp/pkg && tar xzf chess-*.tar.gz
#   cp -r chess-*/chess $(python3 -c "import site; print(site.getsitepackages()[0])")
python3 -m unittest discover tests   # must pass before contributing data
```

## Sharding a stage across 3 nodes

Give each node the same command with a different `--shard i/N`:

```bash
# Pi 4B (4 workers), node 0 of 3 — the ET crossing bracket found by the pilot:
nohup python3 -m twomove.sweep --stage s2b --materials k_n_pawns,k_pawns8 \
  --regimes ET --games 300 --nodes 12000 \
  --out results-shard --workers 4 --shard 0/3 > sweep.log 2>&1 &

# Pi Zero 2W #1 (memory-light: 1 worker), node 1 of 3:
nohup python3 -m twomove.sweep ... --workers 1 --shard 1/3 > sweep.log 2>&1 &
# Pi Zero 2W #2, node 2 of 3:
nohup python3 -m twomove.sweep ... --workers 2 --shard 2/3 > sweep.log 2>&1 &
```

Shard files are named `<point>.s<i>-<N>.jsonl`, so they never collide. Runs are
**resumable**: re-running the same command skips already-recorded game indices.
Then collect and analyze:

```bash
rsync pi4:~/two_move_chess_study/results-shard/*.jsonl merged/
rsync zero1:~/two_move_chess_study/results-shard/*.jsonl merged/
rsync zero2:~/two_move_chess_study/results-shard/*.jsonl merged/
python3 -m twomove.analysis merged --md merged/REPORT.md
```

## Sizing guidance

- **Pi 4B+ (4×A72)**: use `--workers 4`. Expect very roughly 3–8× slower per game
  than a modern x86 core; at `--nodes 3000` that's on the order of 1.5–4 min/game
  per worker — a few hundred games/day sustained. Give it the biggest shard (e.g.
  `0/2` of a 2-way split with both Zeros together as the other half... or 2/4+1/4+1/4
  via `--shard 0/4` + `--shard 1/4` on the Pi 4 run twice).
- **Pi Zero 2W (4×A53, 512 MB)**: `--workers 1` (or 2 if nothing else runs); RAM is
  the constraint — each worker's transposition table is capped (~400k entries) and a
  worker stays under ~150 MB. Prefer lower `--nodes` stages or accept the slower rate.
- Weight shards by node speed: `--shard` slices are equal-sized, so give faster
  nodes several slices (run the command more than once with different `i`).
- Long runs: `nice -n 10` the process; use `tmux` or `systemd-run --user` if you
  want survivable sessions; check progress with `wc -l results-shard/*.jsonl`.

## What to run on the cluster (queue, updated with pilot results)

Pilot verdicts are in `experiments/results/REPORT.md`. In priority order:

1. `s2b` confirmation: `--materials k_n_pawns,k_pawns8 --regimes ET --games 300
   --nodes 12000` — certify the crossing (pilot: 0.562 / 0.531 at 3000 nodes).
2. KC sensitivity: `--stage s2b --materials monster4,k_pawns3 --regimes KC
   --games 100 --nodes 12000` — does "KC never balances" survive stronger defense?
3. `s3` dampers at `--materials knights_pawns,bishops_pawns,no_q_rr --regimes ET
   --games 100` — can nc2/dp2 balance *bigger*, more chess-like armies?
4. `s5` turn order at whichever rung s2b certifies, `--games 200` each order.
5. Budget-sensitivity gate: rerun the certified rung at `--nodes 24000`,
   `--games 100` (plan.md: if the score drifts >10 points toward either side,
   balance is strength-sensitive and the drift direction is itself a finding).

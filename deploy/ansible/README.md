# Deploying the study to your home nodes with Ansible

Run everything from your local computer; the nodes never need GitHub access —
the playbooks ship the code from the checkout they live in, pinned to whatever
revision you have checked out (recorded in `/opt/twomove/app/VERSION` on each node).

## One-time setup (control machine = your computer)

```bash
pip install ansible      # or: apt install ansible / brew install ansible
cd deploy/ansible
cp inventory.example.ini inventory.ini   # edit hosts, users, slices/workers
ansible pis -m ping                      # verify SSH works to all nodes
```

`inventory.ini` is gitignored — your LAN addresses stay local.

## The three playbooks

```bash
ansible-playbook deploy.yml     # provision: packages, code, venv+python-chess
                                # (with the Debian wheel-bug fallback), run the
                                # full test suite on each node, install the
                                # systemd unit. Rerun any time you pull new code.

ansible-playbook sweep.yml      # write the campaign config and start one
                                # twomove-sweep@<slice> service per slice on
                                # each node. Also: -e twomove_sweep_state=stopped
                                # to stop, =restarted to apply a new campaign.

ansible-playbook collect.yml    # fetch all *.jsonl shards to
                                # experiments/results/incoming/, then analyze:
                                # python3 -m twomove.analysis experiments/results/incoming
```

Everything is idempotent: a second `deploy.yml` run reports no changes; a
re-`sweep.yml` on an unchanged campaign leaves running services alone; shard
services **resume** (already-played game indices are skipped) after stop/start
or a power cut, so the Pis can just churn 24/7.

The campaign itself lives in one variable (`twomove_sweep_args` in
`group_vars/all.yml`, currently the S2b confirmation run from
`experiments/DISTRIBUTED.md`). Edit it, `ansible-playbook sweep.yml -e
twomove_sweep_state=restarted`, and the cluster switches jobs. Point new
campaigns at a fresh `--out`-style results dir? Not needed — records are
self-describing (point_id) and analysis groups by it, so one results dir can
hold many campaigns.

Watch a node: `ssh pi4 journalctl -fu twomove-sweep@0`.

## Why not containers (the feasibility probe)

Considered Docker and Podman for the nodes; recommendation is **no containers
here**, for reasons specific to this workload:

1. **Nothing to containerize.** The stack is CPython + two pure-Python packages
   (ours and `python-chess`) — no native builds, no system libs, no version
   matrix. The venv already pins everything a container would pin, and the
   one real packaging wart (Debian's `install_layout` wheel bug) is handled by
   a 6-line fallback in `deploy.yml`.
2. **RAM is the binding constraint on half your fleet.** A Pi Zero 2W has
   512 MB; `dockerd` + `containerd` idle at ~80–120 MB — a 15–25% tax before a
   single game is played, directly shrinking the engine's transposition table.
   Podman avoids the daemon but keeps cost #3.
3. **Multi-arch image logistics.** Zero 2W (aarch64/armv7 depending on OS
   image) + Pi 4 (aarch64) + your x86 control machine means either a registry
   with buildx multi-arch pushes or slow on-device builds — real moving parts,
   recurring maintenance, zero payoff for pure Python.
4. **Idempotence doesn't improve.** systemd units + venv + append-only JSONL
   already restart/resume cleanly; a container wrapper would still need the
   same bind-mounted results dir and the same unit files.

Revisit if the engine ever grows a compiled core (Rust/C): then a prebuilt
multi-arch image (or just prebuilt wheels served from the repo) becomes the
clean way to skip cross-compiling on the Zeros.

**Addendum — Apptainer/Singularity**: assessed separately in
`deploy/apptainer/README.md`. It cures Docker's two disqualifiers (no daemon,
no registry — single-file SIF, rootless) and is the right choice if this study
ever needs citable frozen environments or real HPC time; it stays optional only
because installing Apptainer itself on Raspberry Pi OS currently costs more
than the venv it would replace. A validated definition file is included there.

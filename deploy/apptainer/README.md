# Apptainer/Singularity assessment (HPC-style containers for the Pi fleet)

**Verdict**: Apptainer is the *right* container technology for this fleet — it
dissolves both reasons Docker was rejected — but it stays **optional** because
installing Apptainer itself on Raspberry Pi OS is currently more work than the
entire venv deployment it would replace. Default remains `deploy/ansible/`
(venv + systemd). The definition file here is validated and ready for the day
the trade flips.

## Why Apptainer fits where Docker didn't

`deploy/ansible/README.md` rejected Docker on (1) daemon RAM tax and (2)
multi-arch registry logistics. Apptainer (né Singularity, built for HPC batch):

- **No daemon.** A container is just a child process of the shell/systemd unit
  that starts it. Idle overhead on a 512 MB Zero 2W: ~zero.
- **Rootless.** Runs as the invoking user via user namespaces; result files come
  out owned by you; no root daemon on your LAN.
- **Single-file SIF images.** Build once on the Pi 4B (aarch64), `scp` the .sif
  to the Zeros — same architecture, no registry, no buildx manifests.
- **Bind mounts** keep the append-only JSONL + resume model unchanged.
- **The HPC on-ramp.** If confirmation runs ever outgrow the Pis (university
  cluster, cloud Slurm), SIF is the lingua franca — this def file is the
  ticket. That, plus *environment provenance* (a campaign's REPORT can cite
  `twomove-<gitrev>.sif`, one hash freezing code+python+deps), is the real
  scientific payoff.

## Why it's not the default (July 2026 reality on Raspberry Pi OS)

1. **No easy install on Pi OS.** Apptainer is in Debian *testing/sid* only —
   nothing in bookworm/trixie, which Pi OS tracks; upstream GitHub releases ship
   **amd64 debs only** (arm64 prebuilds are an open request, apptainer#2979);
   the arm64 packages that do exist are in the **Ubuntu PPA** — i.e. you'd run
   Ubuntu Server instead of Pi OS (fine on the 4B, heavy on 512 MB Zeros;
   Ubuntu's own archive also carries `singularity-container` 4.1, which this
   assessment was validated against). Realistic Pi OS route: build the deb once
   from source on the Pi 4B (Go toolchain, upstream `DEBIAN_PACKAGE.md`) and
   install it on all three nodes. One-time, ~30–45 min — but that alone exceeds
   the whole venv deploy.
2. **Requires 64-bit OS fleet-wide.** An aarch64 SIF won't run on 32-bit
   (armhf) Pi OS, common on 512 MB Zeros — and 64-bit CPython itself costs
   ~30–50% more RAM on object-heavy workloads, which is the Zeros' scarcest
   resource. The venv path runs on either.
3. **Pure-Python stack.** The venv already pins everything a SIF would pin;
   the image adds provenance, not capability.

Flip to Apptainer when any of these become true: you want citable frozen
environments per campaign; you get HPC time; the engine grows a compiled core.

## The recipe (when wanted)

```bash
# on the Pi 4B, from the repo root:
sudo apptainer build twomove-$(git rev-parse --short HEAD).sif deploy/apptainer/twomove.def
scp twomove-*.sif zero1:/opt/twomove/ zero2:/opt/twomove/

# run a shard (rootless):
apptainer run --userns --bind /opt/twomove/results:/results /opt/twomove/twomove-<rev>.sif \
    --stage s2b --materials k_n_pawns,k_pawns8 --regimes ET \
    --games 300 --nodes 12000 --out /results --workers 4 --shard 0/4
```

systemd integration is a one-line swap in
`deploy/ansible/templates/twomove-sweep@.service.j2`:

```
ExecStart=/usr/bin/apptainer run --userns --bind ${RESULTS_DIR}:/results /opt/twomove/twomove.sif $SWEEP_ARGS --out /results --workers ${WORKERS} --shard %i/${SHARD_TOTAL}
```

Note the def's `%post` runs the full test suite: **a SIF that builds is a SIF
whose engine passed its gates on that architecture.**

## What was validated (SingularityCE 4.1.1, amd64 sandbox, 2026-07-09)

- Rootfs with the app + vendored `python-chess`: **all 35 tests pass inside
  the container**; sandbox → SIF build; **rootless** (`--userns`, unprivileged
  user) execution of a real sweep shard writing JSONL through a bind mount.
- Not exercised here (environment limits, not design limits): the Docker-Hub
  bootstrap of `twomove.def` (egress proxy blocked registry blobs; a
  debootstrap-bootstrap twin of the def built fine) and an aarch64 build on
  real hardware. Treat `twomove.def`'s first Pi build as its acceptance test.

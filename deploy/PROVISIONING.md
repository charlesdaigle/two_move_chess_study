# Fleet provisioning (reflash guide + design rationale)

Design principle: **nodes are cattle**. Everything of value lives in the git
repo (results, queue, code); noding on a node is worth backing up. Recovery
from any disaster — lost key, dead SD card, bricked OS — is a reflash plus two
playbooks, ~15 minutes. The key-recovery "system" is therefore redundancy +
fast reprovisioning, not backups of private keys.

## OS choice: Raspberry Pi OS Lite **64-bit** (bookworm) on all three

Why this beats the previous mixed fleet (Pi OS on coralreef, 32-bit Ubuntu on
the Zeros):

1. **~1.5–2× faster engine on the Zeros, free.** python-chess is built on
   64-bit bitboards; 32-bit CPython chops those into more, smaller big-int
   digits and pays for it on every move generation. arm64 CPython handles them
   natively. This is the single biggest per-node throughput knob available.
2. **Python 3.11 everywhere** (bookworm) — identical to the version the engine
   was developed and pilot-tested on. No 3.10-vs-3.11 skew between nodes.
3. **Uniform arch + distro** — one ansible behavior, one wheel story, and the
   Apptainer option (deploy/apptainer/) becomes viable fleet-wide if ever
   wanted (aarch64 SIF runs on all three).
4. Lite (headless) idles at ~70–90 MB on a Zero 2W, leaving ~400 MB for the
   worker — comfortable with the TT cap and `MemoryMax=380M`.

RAM math on 512 MB is the only argument for 32-bit, and zram (below) covers it.
Use quality A1/A2-class SD cards if you're buying — 24/7 appends are gentle,
but cheap cards die of everything.

## Flash-time setup (Raspberry Pi Imager, per card)

In Imager: **Raspberry Pi OS Lite (64-bit)** → gear/customization:

| Setting | node1 / node2 | coralreef (only if you reflash it too) |
|---|---|---|
| hostname | `node1` / `node2` (distinct!) | `coralreef` |
| user | `moos-node` + a real password | `cnidarian` + password |
| SSH | enable, **paste BOTH public keys** (laptop + coralreef, one per line) | same |
| Wi-Fi | SSID + PSK (Zeros are Wi-Fi-only) | n/a (ethernet) |

Generate both fleet keys *before* flashing (guarded commands in the next
section) so you can paste the two `.pub` lines together. If your Imager
version only takes one key, paste the laptop's and afterwards run, from the
laptop:

```bash
for h in node1 node2; do
  ssh moos-node@$h 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys' < coralreef.pub
done
```

The password matters: Pi OS keeps LAN password SSH available as the built-in
recovery path — that alone would have turned yesterday's lockout into a
non-event. If you prefer key-only nodes, disable password auth *after* the
fleet keys are installed; the SD-card edit remains the recovery of last resort
either way.

## Fixed IPs via MAC address (do this before anything else)

Reserve an IP for each device **by MAC address** in the router's DHCP
settings. This is the keystone of the setup: reservations bind to hardware,
so they survive reflashes, hostname mistakes, and mDNS/router-DNS roulette
(the node1/node2 confusion seen earlier) — `inventory.ini` then pins
`ansible_host=` to those IPs and never lies.

- Get each MAC without booting anything: it's printed by `ip link` once up,
  but easier — boot each freshly flashed card once and read the router's
  client list, or check the Imager-set hostname there. The Zeros' MAC of
  record is the **Wi-Fi** interface (`wlan0`); coralreef's is ethernet.
- Suggested: keep the current addresses (node1 = 10.0.0.246,
  node2 = 10.0.0.119, plus coralreef's) so the committed inventory stays
  valid.
- Reservation beats static-IP-on-device: one place to manage, no per-node
  netplan/dhcpcd edits, and a reflashed card comes back on the same address
  with zero configuration.

**Reflash gotcha — stale host keys**: a reflashed node presents a new SSH
host key, so the laptop and coralreef will refuse with "REMOTE HOST
IDENTIFICATION HAS CHANGED". Clear the old entries once per machine:

```bash
ssh-keygen -R node1; ssh-keygen -R node2; ssh-keygen -R 10.0.0.246; ssh-keygen -R 10.0.0.119
```

then reconnect once (accept the new fingerprints) before running ansible.

## Key scheme (the robust-but-secure version)

- **Purpose-named keys, never the default path.** On the laptop and on
  coralreef: `~/.ssh/twomove_fleet` (+ `~/.ssh/twomove_deploy` on coralreef for
  GitHub). `ssh-keygen` can then never clobber a key another system trusts —
  yesterday's failure mode is structurally gone.
- **Every node trusts ≥2 keys** (laptop + coralreef), so one lost key never
  locks you out.
- **Public keys are committed to the repo** in `deploy/keys/*.pub`, and
  `provision.yml` installs all of them on every node, additively. Adding a new
  machine to the trust set = commit its `.pub` + run one playbook. This is
  safe: public keys are non-secret by design; the repo never holds private
  material.
- **Private keys are not backed up at all.** Losing one costs: generate a new
  key, commit the pub, reprovision (nodes) or re-add the deploy key in GitHub
  (2 min, revocable). Backing up private keys adds theft surface for less
  recovery value than that. (If you want a copy anyway, a password manager's
  SSH-key vault is the acceptable place — never the repo, never plaintext in
  cloud storage.)

## First boot: two playbooks and done

```bash
# on the laptop (one-time): purpose-named key, guarded against overwrite
[ -f ~/.ssh/twomove_fleet ] || ssh-keygen -t ed25519 -f ~/.ssh/twomove_fleet -N "" -C "laptop fleet key"
cat ~/.ssh/twomove_fleet.pub   # -> commit as deploy/keys/laptop.pub (or ask Claude to)

# on coralreef:
[ -f ~/.ssh/twomove_fleet ] || ssh-keygen -t ed25519 -f ~/.ssh/twomove_fleet -N "" -C "coralreef fleet key"
cp ~/.ssh/twomove_fleet.pub ~/two_move_chess_study/deploy/keys/coralreef.pub
cd ~/two_move_chess_study && git add deploy/keys && git commit -m "fleet public keys" && git push

cd deploy/ansible
ansible-playbook provision.yml   # keys, zram, watchdog, wifi-powersave, journald cap, auto-updates
ansible-playbook deploy.yml      # code, venv, tests, worker units
ansible-playbook agent.yml       # the GitOps loop
```

(`inventory.example.ini` and AUTOMATION.md are updated to use
`~/.ssh/twomove_fleet` via `ansible_ssh_private_key_file`.)

## What provision.yml hardens, and why (24/7-specific)

| Tweak | Why |
|---|---|
| fleet authorized_keys from `deploy/keys/*.pub` | the recovery scheme above |
| **zram swap** (compressed RAM, zstd), SD swapfile disabled | absorbs Python heap spikes on 512 MB without OOM-killing workers or grinding the SD card |
| **hardware watchdog** (`RuntimeWatchdogSec=15`) | a hung kernel reboots itself; workers are `enabled` + resumable, so the node rejoins the campaign unattended |
| **Wi-Fi power save off** on wireless nodes | the Zero 2W's power-saving Wi-Fi drops/lags SSH and rsync on idle links — the classic headless-Zero flakiness |
| journald capped at 32 MB | 24/7 logging must never fill an 8–32 GB card |
| unattended-upgrades | security patches without you thinking about the fleet |

Everything is idempotent — rerun `provision.yml` anytime.

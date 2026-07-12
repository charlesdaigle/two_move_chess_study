# Full-auto mode: the GitOps loop

The repo is the message bus. Campaign specs flow **down** in commits
(`experiments/queue/campaigns.json`); game records flow **up** in commits
(`experiments/results/auto/*.jsonl`). Nobody needs to reach your LAN: Claude
edits the queue and reads results from chat; coralreef reconciles every 15
minutes and drives node1/node2 over local SSH.

```
chat session (Claude)                      your LAN
  edits queue / reads results   git   ┌─ coralreef (controller+worker)
        └── github repo  <──────────►─┤    twomove-agent.timer (15 min):
             branch:                  │    pull → redeploy if code changed →
             claude/two-move-…        │    collect → reconcile (escalation
                                      │    policy) → queue-sync → commit+push
                                      ├─ node1 (worker, slice 2)
                                      └─ node2 (worker, slice 3)
```

The escalation policy (strategy.md, implemented in `twomove/queue.py`) runs on
coralreef: decided points stop at 32 games; ambiguous points double (64, 128),
lift to 12k nodes at 256, certify at 512, strength-gate at 24k; opposite-decided
neighbors on the ET ladder auto-spawn midpoint screens. Every completed tier is
one commit with verdicts embedded in the queue file, so the study's decision
history is the git history.

## One-time setup (you, on coralreef — ~10 minutes)

Fresh SD cards? Follow `deploy/PROVISIONING.md` first (Imager settings, key
scheme, OS choice), then:

```bash
# 0. prerequisites
sudo apt install -y ansible git python3-venv

# 1. deploy key (write access, this repo only). All keygen lines are guarded
#    and purpose-named: they can never overwrite an existing key.
[ -f ~/.ssh/twomove_deploy ] || ssh-keygen -t ed25519 -f ~/.ssh/twomove_deploy -N "" -C "twomove-agent@coralreef"
cat ~/.ssh/twomove_deploy.pub
#    -> GitHub repo -> Settings -> Deploy keys -> Add key, CHECK "Allow write access"
cat >> ~/.ssh/config <<'EOF'
Host github.com
  IdentityFile ~/.ssh/twomove_deploy
  IdentitiesOnly yes
EOF

# 2. repo tracks the fleet branch over SSH
cd ~/two_move_chess_study
git remote set-url origin git@github.com:charlesdaigle/two_move_chess_study.git
git fetch origin && git checkout claude/two-move-chess-balance-mku5j2

# 3. fleet key -> committed to deploy/keys/ (public half only)
[ -f ~/.ssh/twomove_fleet ] || ssh-keygen -t ed25519 -f ~/.ssh/twomove_fleet -N "" -C "coralreef fleet key"
cp ~/.ssh/twomove_fleet.pub deploy/keys/coralreef.pub
git add deploy/keys && git commit -m "coralreef fleet public key" && git push
# (nodes flashed per PROVISIONING.md already trust this key — it was pasted
#  at flash time alongside the laptop's; ssh-copy-id is no longer used)

# 4. inventory + fleet up
cd deploy/ansible
cp inventory.example.ini inventory.ini      # set the DHCP-reserved IPs
ansible pis -m ping                         # all three green?
ansible-playbook provision.yml              # keys, zram, watchdog, wifi, logs
ansible-playbook deploy.yml                 # code + venv + tests on every node
ansible-playbook agent.yml                  # install the 15-min agent timer
```

That's it. Within 15 minutes the agent activates `screen-001` (the T0
screening frontier) and the fleet starts playing. Nothing else is ever run by
hand.

## Watching it

```bash
systemctl list-timers twomove-agent.timer          # next tick
journalctl -u twomove-agent.service -n 30          # last agent run
journalctl -fu twomove-queue@0                     # live games on this node
python3 -m twomove.analysis experiments/results/auto | head -20   # standings
```

From chat, Claude reads the same state after any `git pull` — ask for a status
review anytime, or to reprioritize (edit queue → push → fleet switches within
15 minutes; pause everything by setting the active campaign's status to
`"pending"` and pushing).

## Failure behavior

- Network/GitHub down → agent exits, retries next tick; workers keep playing.
- Node down → its slice stalls; the campaign completes when it returns
  (slices are independent and resumable). Agent keeps committing the others.
- Worker OOM/crash → systemd restarts it in 60 s; it resumes its shard file.
- Two agents/chat racing on the queue → `git pull --rebase` + push-retry;
  worst case a tick is skipped.
- SD-card death → everything of value is in the repo (results committed ≤6 h
  old); reflash, rerun the one-time setup.

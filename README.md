# Two-Move Chess Balance Study

**The axiom**: one player (the *double-mover*) makes two moves per turn; the other
(the *single-mover*) makes one. **The question**: what starting material and rule
modifiers make this game *fair* — a ~50% win rate for each side under good play —
while keeping the starting position recognizably chess-like?

## Documents

| File | Contents |
|---|---|
| `specs/001-two-move-balance/spec.md` | Goal, balance criterion, edge-case rules |
| `specs/001-two-move-balance/research.md` | Theory: prior art (Monster/Marseillais/Progressive chess), tempo-annuity & threat-parity analysis, hypotheses H1–H6, the ruleset parameter space |
| `specs/001-two-move-balance/plan.md` | Architecture, engine design, sweep stages S0–S5, statistics, distributed (Raspberry Pi) mode |
| `specs/001-two-move-balance/tasks.md` | Task breakdown and status |
| `experiments/results/` | Committed pilot data (JSONL) and reports — findings in `REPORT.md` |
| `experiments/DISTRIBUTED.md` | Sharding model + manual node setup reference |
| `deploy/ansible/` | Idempotent Ansible deployment for home compute nodes (Pi cluster): deploy / sweep / collect playbooks |

## Quick start

```bash
# python-chess is the only dependency (pure Python).
pip install chess            # if the wheel build fails, see DISTRIBUTED.md §Install

python -m unittest discover tests            # 32 tests: rules edge cases + engine gates

# Engine validation gates (do not trust sweep numbers until these pass):
python -m twomove.sweep --stage s0 --games 16 --nodes 2000 --out experiments/results/gates
python -m twomove.analysis experiments/results/gates

# Pilot: symmetric-material blowout check + the material ladder:
python -m twomove.sweep --stage s1 --games 24 --nodes 3000 --out experiments/results/pilot
python -m twomove.sweep --stage s2 --games 32 --nodes 3000 --out experiments/results/pilot
python -m twomove.analysis experiments/results/pilot --md experiments/results/pilot/REPORT.md
```

## The game, in brief

Default ("ET", Marseillais-style) rules: each half-move must be legal orthodox chess;
if the double-mover's **first** half-move gives check, their turn ends immediately;
a double-mover with no legal second half-move simply passes it; en passant applies
only against the immediately preceding half-move; threefold repetition, a 100
half-move no-progress rule, and a game cap give draws. The "KC" regime instead plays
Monster-chess style: checks are not enforced, capture the king to win. Sweepable
modifiers: `nc2` (no capture on the second half-move), `dp2` (second half-move must
move a different piece), `k` (double move only every k-th turn), turn order, and the
double-mover's starting army (`twomove/rules.py: MATERIAL_SCHEMES`, from the full
army down to Monster chess's king + 4 pawns).

## Why a custom engine

No existing engine (Stockfish, Fairy-Stockfish, Lc0) supports multi-move turns, and
balance measurements move with engine strength — both sides must run the *same*
search under fixed node budgets. `twomove/engine.py` searches the half-move tree
with owner-based max/min (no sign flip inside a double turn), schedule-aware
quiescence with evasion nodes (so the KC king is never hung behind the horizon),
a transposition table, and seeded root-softmax opening diversification.

#!/usr/bin/env bash
# Perturbation study — evolve standard chess one knob at a time.
#
# Unattended run on ocean (~12-16h). Every point is an independent trial: take
# standard chess + the two-move axiom (a known 1.000 blowout) and change ONE
# thing (a damper, a doubling period, a turn-order flip, one piece removed), or
# TWO things, and measure where the double-mover's score lands.
#
# Resumable: twomove.sweep skips game indices already recorded, so re-running
# this script continues where it stopped. Results + a regenerated REPORT.md are
# committed after every sub-batch.
#
# Launch:  nohup timeout 18h bash experiments/perturbation/run.sh >/dev/null 2>&1 &

set -u
cd "$(dirname "$0")/../.." || exit 1

PY=.venv/bin/python
OUT=experiments/results/perturbation
LOG="$OUT/driver.log"
N=384          # games/point -> Wilson 95% CI half-width ~0.05
NODES=8000     # strong enough that verdicts don't flip vs 12k (pilot showed 3k does)
W=20           # ocean worker processes
mkdir -p "$OUT"

say() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

commit() {
  "$PY" -m twomove.analysis "$OUT" --md "$OUT/REPORT.md" >>"$LOG" 2>&1 || true
  git add -A "$OUT" experiments/perturbation 2>/dev/null
  git -c user.name="Charles Daigle" \
      -c user.email="69538719+charlesdaigle@users.noreply.github.com" \
      commit -q -m "perturbation study: progress $(date -Is)" 2>/dev/null \
    && (git push -q 2>>"$LOG" || say "push failed (committed locally)")
}

run() {  # run <tag> <sweep args...>
  local tag=$1; shift
  say "START $tag  ::  $*"
  "$PY" -m twomove.sweep "$@" --games "$N" --nodes "$NODES" --out "$OUT" --workers "$W" \
    >>"$LOG" 2>&1 || say "sweep $tag exited nonzero (continuing)"
  say "DONE  $tag"
  commit
}

MAT_TRIM="no_q,no_r,no_rr,no_nn,no_bb,no_q_r,no_q_rr"
MAT_ALL="full_p7,full_p6,no_n,no_b,no_r,no_nn,no_bb,no_rr,no_q,no_q_n,no_q_b,no_q_nn,no_q_bb,no_q_r,no_q_rr"

say "=== perturbation study begins (N=$N, nodes=$NODES) ==="

# Most informative first; full-material blowout refs last so a timeout loses least.
run B_s3_trim_damper  --stage s3 --materials "$MAT_TRIM" --regimes ET,IL   # trim x {nc2,dp2,both}
run B_s4_trim_k2      --stage s4 --materials no_q,no_r,no_rr,no_nn,no_q_r --regimes ET,IL
run A_s2_material     --stage s2 --materials "$MAT_ALL" --regimes ET,IL     # one piece off, no damper
run A_s3_full_damper  --stage s3 --materials full --regimes ET,IL          # standard + one damper
run A_s4_full_k2      --stage s4 --materials full --regimes ET,IL
run B_s5_trim_order   --stage s5 --materials no_q,no_r,no_rr --regimes ET
run A_s5_full_order    --stage s5 --materials full --regimes ET
run A_s1_refs         --stage s1 --regimes ET,IL                            # baseline blowouts

say "=== ALL BATCHES COMPLETE ==="
commit
touch "$OUT/DONE"

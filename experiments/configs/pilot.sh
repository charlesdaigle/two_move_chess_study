#!/bin/bash
# Pilot stage commands (cloud, 4 workers). Confirmation-stage commands for the
# Pi cluster are in experiments/DISTRIBUTED.md.
set -e
cd "$(dirname "$0")/../.."

python3 -m twomove.sweep --stage s1 --games 24 --nodes 3000 \
    --out experiments/results/pilot --workers 4
python3 -m twomove.sweep --stage s2 --games 32 --nodes 3000 \
    --out experiments/results/pilot --workers 4
python3 -m twomove.analysis experiments/results/pilot \
    --md experiments/results/pilot/REPORT.md \
    --csv experiments/results/pilot/results.csv

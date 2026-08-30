# Sweep results (double-mover score)

Sorted by distance from 50%. `balanced` = Wilson CI within [0.40,0.60] and score within [0.45,0.55] (spec.md criterion, tau=0.05 needs N>~384).

| label | point | N | W/D/L | score | 95% CI | Elo | med.len | terminations | balanced |
|---|---|---|---|---|---|---|---|---|---|
| s0scaleS-k_pawns6-KC | `mat=k_pawns6\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=search\|ns=4000\|es=search` | 16 | 13/1/2 | 0.844 | [0.604, 0.950] | +293 | 15 | king_capture:15, repetition:1 | no |
| s0scaleD-k_pawns6-KC | `mat=k_pawns6\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=4000\|e=search\|ns=2000\|es=search` | 16 | 14/1/1 | 0.906 | [0.677, 0.978] | +394 | 10 | king_capture:15, repetition:1 | no |
| s0vsrandD-k_pawns6-ET | `mat=k_pawns6\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=random\|ns=2000\|es=search` | 16 | 0/0/16 | 0.000 | [0.000, 0.194] | -2400 | 15 | checkmate:16 | no |
| s0vsrandS-k_pawns6-ET | `mat=k_pawns6\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=search\|ns=2000\|es=random` | 16 | 16/0/0 | 1.000 | [0.806, 1.000] | +2400 | 16 | checkmate:16 | no |
| s0vsrandD-monster4-KC | `mat=monster4\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=random\|ns=2000\|es=search` | 16 | 0/0/16 | 0.000 | [0.000, 0.194] | -2400 | 9 | king_capture:16 | no |
| s0vsrandS-monster4-KC | `mat=monster4\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=search\|ns=2000\|es=random` | 16 | 16/0/0 | 1.000 | [0.806, 1.000] | +2400 | 5 | king_capture:16 | no |
| s0vsrandD-no_q_rr-ET | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=random\|ns=2000\|es=search` | 16 | 0/0/16 | 0.000 | [0.000, 0.194] | -2400 | 22 | checkmate:16 | no |
| s0vsrandS-no_q_rr-ET | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=search\|ns=2000\|es=random` | 16 | 16/0/0 | 1.000 | [0.806, 1.000] | +2400 | 15 | checkmate:16 | no |
| s0scaleS-no_q_rr-ET | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=2000\|e=search\|ns=4000\|es=search` | 16 | 16/0/0 | 1.000 | [0.806, 1.000] | +2400 | 21 | checkmate:16 | no |
| s0scaleD-no_q_rr-ET | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=4000\|e=search\|ns=2000\|es=search` | 16 | 16/0/0 | 1.000 | [0.806, 1.000] | +2400 | 16 | checkmate:16 | no |

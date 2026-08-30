# Sweep results (double-mover score)

Sorted by distance from 50%. `balanced` = Wilson CI within [0.40,0.60] and score within [0.45,0.55] (spec.md criterion, tau=0.05 needs N>~384).

| label | point | N | W/D/L | score | 95% CI | Elo | med.len | terminations | balanced |
|---|---|---|---|---|---|---|---|---|---|
| s2-k_pawns8-ET | `mat=k_pawns8\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 16/2/14 | 0.531 | [0.364, 0.691] | +22 | 25 | checkmate:30, repetition:2 | no |
| s2-k_n_pawns-ET | `mat=k_n_pawns\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 18/0/14 | 0.562 | [0.393, 0.718] | +44 | 29 | checkmate:32 | no |
| s2-bishops_pawns-ET | `mat=bishops_pawns\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 23/4/5 | 0.781 | [0.612, 0.890] | +221 | 26 | checkmate:28, repetition:4 | no |
| s2-k_pawns6-ET | `mat=k_pawns6\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 4/2/26 | 0.156 | [0.069, 0.318] | -293 | 22 | checkmate:30, repetition:1, stalemate:1 | no |
| s2-monster4-ET | `mat=monster4\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 4/1/27 | 0.141 | [0.059, 0.299] | -314 | 20 | checkmate:31, repetition:1 | no |
| s2-k_pawns3-KC | `mat=k_pawns3\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 28/1/3 | 0.891 | [0.738, 0.959] | +364 | 16 | king_capture:31, repetition:1 | no |
| s2-monster4-KC | `mat=monster4\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 29/0/3 | 0.906 | [0.758, 0.968] | +394 | 14 | king_capture:32 | no |
| s2-k_pawns6-KC | `mat=k_pawns6\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 30/2/0 | 0.969 | [0.843, 0.995] | +596 | 15 | king_capture:30, repetition:2 | no |
| s2-knights_pawns-ET | `mat=knights_pawns\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 31/0/1 | 0.969 | [0.843, 0.995] | +596 | 25 | checkmate:32 | no |
| s2-k_pawns3-ET | `mat=k_pawns3\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 0/1/31 | 0.016 | [0.002, 0.133] | -720 | 22 | checkmate:31, repetition:1 | no |
| s2-k_pawns8-KC | `mat=k_pawns8\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 31/1/0 | 0.984 | [0.867, 0.998] | +720 | 13 | king_capture:31, repetition:1 | no |
| s2-bishops_pawns-KC | `mat=bishops_pawns\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 5 | king_capture:32 | no |
| s1-full-ET | `mat=full\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 24 | 24/0/0 | 1.000 | [0.862, 1.000] | +2400 | 9 | checkmate:24 | no |
| s1-full-IL | `mat=full\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 24 | 24/0/0 | 1.000 | [0.862, 1.000] | +2400 | 6 | checkmate:24 | no |
| s1-full-KC | `mat=full\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 24 | 24/0/0 | 1.000 | [0.862, 1.000] | +2400 | 2 | king_capture:24 | no |
| s2-k_n_pawns-KC | `mat=k_n_pawns\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 2 | king_capture:32 | no |
| s2-knights_pawns-KC | `mat=knights_pawns\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 3 | king_capture:32 | no |
| s2-no_q_rr-ET | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 21 | checkmate:32 | no |
| s2-no_q_rr-KC | `mat=no_q_rr\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 3 | king_capture:32 | no |
| s2-no_q_r-ET | `mat=no_q_r\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 17 | checkmate:32 | no |
| s2-no_q_r-KC | `mat=no_q_r\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 3 | king_capture:32 | no |
| s2-no_q-ET | `mat=no_q\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 17 | checkmate:32 | no |
| s2-no_q-KC | `mat=no_q\|reg=KC\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=3000\|e=search` | 32 | 32/0/0 | 1.000 | [0.893, 1.000] | +2400 | 4 | king_capture:32 | no |

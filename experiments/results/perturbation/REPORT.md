# Sweep results (double-mover score)

Sorted by distance from 50%. `balanced` = Wilson CI within [0.40,0.60] and score within [0.45,0.55] (spec.md criterion, tau=0.05 needs N>~384).

| label | point | N | W/D/L | score | 95% CI | Elo | med.len | terminations | balanced |
|---|---|---|---|---|---|---|---|---|---|
| s3-no_q_rr-ET-nc2-dp2 | `mat=no_q_rr\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 184/30/170 | 0.518 | [0.468, 0.568] | +13 | 30 | checkmate:354, repetition:22, no_progress:8 | **YES** |
| s3-no_q_rr-IL-dp2 | `mat=no_q_rr\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 198/27/159 | 0.551 | [0.501, 0.600] | +35 | 29 | checkmate:357, repetition:22, no_progress:5 | no |
| s3-no_q_rr-ET-dp2 | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 212/29/143 | 0.590 | [0.540, 0.638] | +63 | 27 | checkmate:355, repetition:25, no_progress:4 | no |
| s3-no_q_rr-IL-nc2-dp2 | `mat=no_q_rr\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 130/28/226 | 0.375 | [0.328, 0.424] | -89 | 32 | checkmate:356, repetition:24, no_progress:4 | no |
| s3-no_q_r-IL-nc2-dp2 | `mat=no_q_r\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 260/21/103 | 0.704 | [0.657, 0.748] | +151 | 31 | checkmate:363, repetition:17, no_progress:4 | no |
| s3-no_q_r-ET-nc2-dp2 | `mat=no_q_r\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 306/23/55 | 0.827 | [0.786, 0.861] | +272 | 27 | checkmate:361, repetition:16, no_progress:7 | no |
| s3-no_q_r-ET-dp2 | `mat=no_q_r\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 310/16/58 | 0.828 | [0.787, 0.863] | +273 | 25 | checkmate:368, repetition:16 | no |
| s3-no_q_r-IL-dp2 | `mat=no_q_r\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 311/26/47 | 0.844 | [0.804, 0.877] | +293 | 24 | checkmate:358, repetition:17, no_progress:9 | no |
| s3-no_q_rr-IL-nc2 | `mat=no_q_rr\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 331/20/33 | 0.888 | [0.853, 0.916] | +360 | 26 | checkmate:364, repetition:16, no_progress:3, stalemate:1 | no |
| s3-no_rr-IL-nc2-dp2 | `mat=no_rr\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 338/15/31 | 0.900 | [0.866, 0.926] | +381 | 21 | checkmate:369, repetition:11, no_progress:3, stalemate:1 | no |
| s3-no_q-IL-nc2-dp2 | `mat=no_q\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 346/15/23 | 0.921 | [0.889, 0.944] | +426 | 27 | checkmate:369, repetition:13, no_progress:2 | no |
| s3-no_nn-IL-nc2-dp2 | `mat=no_nn\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 352/10/22 | 0.930 | [0.900, 0.951] | +448 | 20 | checkmate:374, repetition:9, no_progress:1 | no |
| s3-no_bb-IL-nc2-dp2 | `mat=no_bb\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 348/19/17 | 0.931 | [0.901, 0.952] | +452 | 22 | checkmate:365, repetition:18, no_progress:1 | no |
| s3-no_nn-ET-nc2-dp2 | `mat=no_nn\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 354/10/20 | 0.935 | [0.906, 0.956] | +463 | 18 | checkmate:374, repetition:7, no_progress:2, stalemate:1 | no |
| s3-no_q_rr-ET-nc2 | `mat=no_q_rr\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 355/10/19 | 0.938 | [0.909, 0.958] | +470 | 24 | checkmate:374, repetition:10 | no |
| s3-no_rr-IL-dp2 | `mat=no_rr\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 356/9/19 | 0.939 | [0.910, 0.959] | +474 | 11 | checkmate:375, repetition:6, no_progress:3 | no |
| s3-no_nn-ET-dp2 | `mat=no_nn\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 361/7/16 | 0.949 | [0.922, 0.967] | +509 | 13 | checkmate:377, repetition:7 | no |
| s3-no_bb-ET-nc2-dp2 | `mat=no_bb\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 361/11/12 | 0.954 | [0.929, 0.971] | +528 | 17 | checkmate:373, repetition:8, no_progress:3 | no |
| s3-no_rr-ET-dp2 | `mat=no_rr\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 365/4/15 | 0.956 | [0.930, 0.972] | +534 | 11 | checkmate:380, repetition:3, no_progress:1 | no |
| s3-no_rr-ET-nc2-dp2 | `mat=no_rr\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 365/5/14 | 0.957 | [0.932, 0.973] | +539 | 14 | checkmate:379, repetition:4, no_progress:1 | no |
| s3-no_q-ET-nc2-dp2 | `mat=no_q\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 361/14/9 | 0.958 | [0.933, 0.974] | +545 | 24 | checkmate:370, repetition:10, no_progress:4 | no |
| s3-no_nn-IL-dp2 | `mat=no_nn\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 366/5/13 | 0.960 | [0.935, 0.975] | +550 | 13 | checkmate:379, repetition:4, no_progress:1 | no |
| s3-no_q-IL-dp2 | `mat=no_q\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 368/5/11 | 0.965 | [0.941, 0.979] | +575 | 21 | checkmate:379, repetition:4, no_progress:1 | no |
| s3-no_bb-ET-dp2 | `mat=no_bb\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 370/2/12 | 0.966 | [0.943, 0.980] | +582 | 13 | checkmate:382, no_progress:1, repetition:1 | no |
| s4-no_q_r-ET-k2 | `mat=no_q_r\|reg=ET\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 368/6/10 | 0.966 | [0.943, 0.980] | +582 | 28 | checkmate:378, repetition:5, no_progress:1 | no |
| s3-no_q-ET-dp2 | `mat=no_q\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 370/4/10 | 0.969 | [0.946, 0.982] | +596 | 21 | checkmate:380, repetition:4 | no |
| s3-no_bb-IL-dp2 | `mat=no_bb\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 370/5/9 | 0.970 | [0.948, 0.983] | +604 | 14 | checkmate:379, repetition:5 | no |
| s3-no_r-IL-nc2-dp2 | `mat=no_r\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 370/6/8 | 0.971 | [0.949, 0.984] | +612 | 18 | checkmate:378, repetition:4, no_progress:2 | no |
| s3-no_r-ET-nc2-dp2 | `mat=no_r\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 372/4/8 | 0.974 | [0.953, 0.986] | +629 | 14 | checkmate:380, repetition:3, no_progress:1 | no |
| s4-no_q_r-IL-k2 | `mat=no_q_r\|reg=IL\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 376/2/6 | 0.982 | [0.963, 0.991] | +692 | 28 | checkmate:382, repetition:2 | no |
| s2-no_q_rr-ET | `mat=no_q_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 377/3/4 | 0.986 | [0.968, 0.994] | +735 | 19 | checkmate:381, repetition:3 | no |
| s4-no_q-ET-k2 | `mat=no_q\|reg=ET\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 379/0/5 | 0.987 | [0.970, 0.994] | +752 | 25 | checkmate:384 | no |
| s2-no_q_rr-IL | `mat=no_q_rr\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 379/1/4 | 0.988 | [0.972, 0.995] | +770 | 18 | checkmate:383, repetition:1 | no |
| s3-no_r-ET-dp2 | `mat=no_r\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 378/3/3 | 0.988 | [0.972, 0.995] | +770 | 10 | checkmate:381, repetition:3 | no |
| s4-no_r-ET-k2 | `mat=no_r\|reg=ET\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 380/0/4 | 0.990 | [0.974, 0.996] | +791 | 14 | checkmate:384 | no |
| s3-full-IL-dp2 | `mat=full\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 380/1/3 | 0.991 | [0.975, 0.997] | +814 | 12 | checkmate:383, repetition:1 | no |
| s3-no_q_r-IL-nc2 | `mat=no_q_r\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 378/5/1 | 0.991 | [0.975, 0.997] | +814 | 23 | checkmate:379, repetition:4, no_progress:1 | no |
| s3-no_r-IL-dp2 | `mat=no_r\|reg=IL\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 380/1/3 | 0.991 | [0.975, 0.997] | +814 | 12 | checkmate:383, repetition:1 | no |
| s4-full-ET-k2 | `mat=full\|reg=ET\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 381/0/3 | 0.992 | [0.977, 0.997] | +842 | 14 | checkmate:384 | no |
| s4-no_q-IL-k2 | `mat=no_q\|reg=IL\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 380/2/2 | 0.992 | [0.977, 0.997] | +842 | 26 | checkmate:382, no_progress:1, repetition:1 | no |
| s2-no_q_r-ET | `mat=no_q_r\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 381/1/2 | 0.994 | [0.979, 0.998] | +873 | 16 | checkmate:383, repetition:1 | no |
| s3-full-ET-nc2-dp2 | `mat=full\|reg=ET\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/0/2 | 0.995 | [0.981, 0.999] | +912 | 14 | checkmate:384 | no |
| s3-no_nn-ET-nc2 | `mat=no_nn\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/0/2 | 0.995 | [0.981, 0.999] | +912 | 13 | checkmate:384 | no |
| s4-no_nn-IL-k2 | `mat=no_nn\|reg=IL\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/0/2 | 0.995 | [0.981, 0.999] | +912 | 15 | checkmate:384 | no |
| s2-no_q_nn-IL | `mat=no_q_nn\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/0/2 | 0.995 | [0.981, 0.999] | +912 | 16 | checkmate:384 | no |
| s4-no_rr-IL-k2 | `mat=no_rr\|reg=IL\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/0/2 | 0.995 | [0.981, 0.999] | +912 | 14 | checkmate:384 | no |
| s3-full-ET-dp2 | `mat=full\|reg=ET\|nc2=0\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/1/1 | 0.996 | [0.983, 0.999] | +963 | 12 | checkmate:383, no_progress:1 | no |
| s3-full-IL-nc2-dp2 | `mat=full\|reg=IL\|nc2=1\|dp2=1\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/1/1 | 0.996 | [0.983, 0.999] | +963 | 17 | checkmate:383, repetition:1 | no |
| s4-no_r-IL-k2 | `mat=no_r\|reg=IL\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/1/1 | 0.996 | [0.983, 0.999] | +963 | 15 | checkmate:383, repetition:1 | no |
| s4-full-IL-k2 | `mat=full\|reg=IL\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 14 | checkmate:384 | no |
| s3-full-IL-nc2 | `mat=full\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 13 | checkmate:384 | no |
| s2-no_bb-ET | `mat=no_bb\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 9 | checkmate:384 | no |
| s4-no_nn-ET-k2 | `mat=no_nn\|reg=ET\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 16 | checkmate:384 | no |
| s2-no_nn-IL | `mat=no_nn\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 8 | checkmate:384 | no |
| s3-no_nn-IL-nc2 | `mat=no_nn\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 15 | checkmate:384 | no |
| s2-no_q_bb-ET | `mat=no_q_bb\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 17 | checkmate:384 | no |
| s2-no_q_bb-IL | `mat=no_q_bb\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 17 | checkmate:384 | no |
| s2-no_q_nn-ET | `mat=no_q_nn\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 16 | checkmate:384 | no |
| s2-no_q_n-IL | `mat=no_q_n\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 16 | checkmate:384 | no |
| s3-no_q_r-ET-nc2 | `mat=no_q_r\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 382/2/0 | 0.997 | [0.985, 1.000] | +1033 | 20 | checkmate:382, repetition:2 | no |
| s2-no_q_r-IL | `mat=no_q_r\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 16 | checkmate:384 | no |
| s2-no_q-ET | `mat=no_q\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 768 | 766/0/2 | 0.997 | [0.991, 0.999] | +1033 | 15 | checkmate:768 | no |
| s3-no_rr-ET-nc2 | `mat=no_rr\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/0/1 | 0.997 | [0.985, 1.000] | +1033 | 11 | checkmate:384 | no |
| s2-no_b-ET | `mat=no_b\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/1/0 | 0.999 | [0.988, 1.000] | +1154 | 8 | checkmate:383, repetition:1 | no |
| s2-no_q_b-ET | `mat=no_q_b\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/1/0 | 0.999 | [0.988, 1.000] | +1154 | 17 | checkmate:383, repetition:1 | no |
| s3-no_q-ET-nc2 | `mat=no_q\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/1/0 | 0.999 | [0.988, 1.000] | +1154 | 19 | checkmate:383, repetition:1 | no |
| s3-no_q-IL-nc2 | `mat=no_q\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/1/0 | 0.999 | [0.988, 1.000] | +1154 | 20 | checkmate:383, no_progress:1 | no |
| s4-no_rr-ET-k2 | `mat=no_rr\|reg=ET\|nc2=0\|dp2=0\|k=2\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/1/0 | 0.999 | [0.988, 1.000] | +1154 | 14 | checkmate:383, repetition:1 | no |
| s3-no_rr-IL-nc2 | `mat=no_rr\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 383/1/0 | 0.999 | [0.988, 1.000] | +1154 | 13 | checkmate:383, no_progress:1 | no |
| s2-no_rr-ET | `mat=no_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 768 | 767/1/0 | 0.999 | [0.994, 1.000] | +1274 | 7 | checkmate:767, repetition:1 | no |
| s2-full_p6-ET | `mat=full_p6\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 7 | checkmate:384 | no |
| s2-full_p6-IL | `mat=full_p6\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 6 | checkmate:384 | no |
| s2-full_p7-ET | `mat=full_p7\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 7 | checkmate:384 | no |
| s2-full_p7-IL | `mat=full_p7\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 6 | checkmate:384 | no |
| s5-full-ET-firstB | `mat=full\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=B\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 7 | checkmate:384 | no |
| s5-full-ET | `mat=full\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 7 | checkmate:384 | no |
| s3-full-ET-nc2 | `mat=full\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 11 | checkmate:384 | no |
| s3-no_bb-ET-nc2 | `mat=no_bb\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 12 | checkmate:384 | no |
| s2-no_bb-IL | `mat=no_bb\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s3-no_bb-IL-nc2 | `mat=no_bb\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 15 | checkmate:384 | no |
| s2-no_b-IL | `mat=no_b\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s2-no_nn-ET | `mat=no_nn\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s2-no_n-ET | `mat=no_n\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s2-no_n-IL | `mat=no_n\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s2-no_q_b-IL | `mat=no_q_b\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 16 | checkmate:384 | no |
| s2-no_q_n-ET | `mat=no_q_n\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 16 | checkmate:384 | no |
| s5-no_q-ET-firstB | `mat=no_q\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=B\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 16 | checkmate:384 | no |
| s2-no_q-IL | `mat=no_q\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 15 | checkmate:384 | no |
| s5-no_rr-ET-firstB | `mat=no_rr\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=B\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s2-no_rr-IL | `mat=no_rr\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 7 | checkmate:384 | no |
| s5-no_r-ET-firstB | `mat=no_r\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=B\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 7 | checkmate:384 | no |
| s2-no_r-ET | `mat=no_r\|reg=ET\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 768 | 768/0/0 | 1.000 | [0.995, 1.000] | +2400 | 7 | checkmate:768 | no |
| s3-no_r-ET-nc2 | `mat=no_r\|reg=ET\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 11 | checkmate:384 | no |
| s2-no_r-IL | `mat=no_r\|reg=IL\|nc2=0\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 8 | checkmate:384 | no |
| s3-no_r-IL-nc2 | `mat=no_r\|reg=IL\|nc2=1\|dp2=0\|k=1\|dbl=W\|first=W\|n=8000\|e=search` | 384 | 384/0/0 | 1.000 | [0.990, 1.000] | +2400 | 12 | checkmate:384 | no |

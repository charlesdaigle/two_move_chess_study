# Pilot Findings: Where Two-Move Chess Balances

**Data**: S0 gates (160 games) + S1 blowout (72) + S2 ladder (672), engine =
`twomove` alpha-beta @ 3000 nodes/half-move, 32 games/point, turn order alternated.
Raw JSONL: `experiments/results/{gates,pilot}/`. Tables: `pilot/REPORT_TABLE.md`,
`pilot/results.csv`. All numbers are the **double-mover's** score.

## Headline results

| Rung (double-mover army) | ~pawns | KC score | ET score |
|---|---|---|---|
| full army | 40 | 1.000 | 1.000 |
| minus queen (`no_q`) | 30.5 | 1.000 | 1.000 |
| minus Q+R (`no_q_r`) | 25.5 | 1.000 | 1.000 |
| minus Q+2R (`no_q_rr`) | 20.5 | 1.000 | 1.000 |
| K+2B+8P (`bishops_pawns`) | 14.5 | 1.000 | 0.781 |
| K+2N+8P (`knights_pawns`) | 14 | 1.000 | **0.969** |
| K+N+8P (`k_n_pawns`) | 11 | 1.000 | **0.562** ⟵ |
| K+8P (`k_pawns8`) | 8 | 0.984 | **0.531** ⟵ |
| K+6P (`k_pawns6`) | 6 | 0.969 | 0.156 |
| K+4P (`monster4`, = Monster chess) | 4 | 0.906 | 0.141 |
| K+3P (`k_pawns3`) | 3 | 0.891 | 0.016 |

## Findings

1. **H1 confirmed — the raw axiom is a total blowout.** With equal armies the
   double-mover scored 72/72 across all three check regimes; under king-capture
   rules the median game lasted **2 rounds**. No material handicap is needed to
   see this; every regime needs one.

2. **King-capture (Monster) semantics cannot be balanced by material alone.**
   The KC ladder never crosses 50% — even **king + 3 pawns beats the full orthodox
   army 89%** of the time at pilot strength. Mechanisms visible in the games: the
   double-mover's king is effectively uncapturable (moves twice, transits attacked
   squares), pawn pairs promote in 3 turns, and every turn can stack two king-capture
   threats while one reply parries one. Monster chess itself (K+4P) came out **0.906
   for the monster** — the folk "roughly playable" assessment looks generous to the
   defender at engine level. *Caveat*: research.md §5 predicts weak defense inflates
   the double-mover; the 4x-budget sensitivity gate on these rungs is queued.

3. **Marseillais check rules (ET) are the load-bearing damper — and they work.**
   The single rule "a first half-move that gives check ends your turn" moves the
   balance point from "below K+3P" up to **king + knight + 8 pawns**. The ET ladder
   crosses 50% between `knights_pawns` (0.969) and `k_pawns6` (0.156), with two
   near-balanced rungs in between:
   - **K+N+8P: 0.562** [0.393, 0.718]
   - **K+8P: 0.531** [0.364, 0.691]
   These are the **candidate balanced rulesets** (spec criterion needs N≥~384 to
   certify τ=0.05; that is the S2b confirmation job).

4. **Knights beat bishops as double-move pieces — theory P3 validated, and the
   ladder is non-monotone.** At equal nominal material, K+2N+8P scored **0.969**
   vs K+2B+8P's **0.781**. A knight moving twice covers the 5×5 box (a short-range
   queen); two bishops don't compound the same way. Consequence: material value
   under this axiom is *not* orthodox value, and bisection must respect the
   potency ordering, not pawn counts.

5. **Balance lives on a cliff.** Under ET, the two flank pawns between K+8P (0.531)
   and K+6P (0.156) are worth ~0.37 of score; one knight (K+N+8P → K+2N+8P) is
   worth ~0.41. Fine-tuning between rungs will need the softer knobs — turn order
   (S5), dampers `nc2`/`dp2` (S3, which should let *larger, more chess-like* armies
   balance), or doubling period (S4).

6. **Near-balanced games look like real games.** Median length at the crossing:
   25–29 rounds, decisive by checkmate ≥94%, draws ≤6%, one stalemate in 672 games.
   The race structure prediction (H5) held: no cap-outs, low draw rates.

## Hypothesis scoreboard (pilot strength)

| | Verdict |
|---|---|
| H1 blowout | **Confirmed** (72/72, all regimes) |
| H2 KC crossing near Monster | **Refuted** — no KC crossing anywhere on the ladder |
| H3 ET lifts the crossing | **Confirmed in direction**, magnitude larger than guessed: crossing at 8–11 pawns, not ~20 |
| H4 dampers buy back material | Untested (S3 queued) |
| H5 race structure | **Confirmed** (short decisive games, draws <10%) |
| H6 turn-order value | Untested (S5 queued) |
| P3 knight > bishop potency | **Confirmed** (0.969 vs 0.781) |

## Next runs (Pi cluster queue, see DISTRIBUTED.md)

1. **S2b confirm** `--materials k_n_pawns,k_pawns8 --regimes ET --games 300
   --nodes 12000` — certify (or move) the crossing at 4× strength.
2. **Sensitivity gate** on `monster4`/`k_pawns3` under KC at `--nodes 12000`:
   does the KC no-crossing result survive stronger defense?
3. **S3 dampers** `--materials knights_pawns,bishops_pawns,no_q_rr --regimes ET`:
   can `nc2`/`dp2` make *bigger* armies (more recognizable chess) balance?
4. **S5 turn order** at whichever rung S2b certifies.

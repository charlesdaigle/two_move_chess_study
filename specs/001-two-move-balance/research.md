# Research: The Theory of Two-Move Chess Balance

**Status**: Phase 0 complete — this document sets up the empirical study.
**Companion**: `spec.md` (goal), `plan.md` (how we test what this document predicts).

---

## 1. Prior art: what is already known

The two-move axiom is not new; three families of existing variants bracket our design
space and give us priors for where balance lives.

### 1.1 Monster chess (the closest ancestor)
**Monster chess** ("Super King"): White has **king + the four center pawns
(c2, d2, e2, f2)** and makes **two moves every turn**; Black has the **full orthodox
army** and moves once. Win by **capturing the king** — check and checkmate are not
enforced as constraints, so the monster king may step "through" attacked squares as long
as it isn't actually captured, and Black must never end a turn where White can capture
the Black king within two half-moves.

This is exactly our axiom with one particular material scheme and one particular check
regime. Folk assessment (it has never been solved) is that the game is *playable* and
that the monster side is dangerous out of proportion to its ~4 pawns of material — most
sources consider the monster favored or near-even against unprepared opponents. Two
structural observations from Monster chess carry over:

- **The double-mover's king is nearly unmatable.** It moves two squares a turn, can
  capture an attacker and step away in one turn, and under king-capture semantics can
  transit attacked squares. The single-mover essentially cannot deliver mate with few
  pieces; they win by **annihilation** (capturing everything, especially with the queen
  from range) rather than by mating attack.
- **The single-mover's king is desperately fragile.** Any position where the
  double-mover can create two half-move-deep threats against it is lost, because one
  reply parries at most one threat.

**Prior extracted**: under king-capture semantics, balance sits at an *extreme* material
handicap — around **king + 4–6 pawns vs. the full army**, i.e. the double-move is worth
on the order of **30+ pawns of material equivalent**.

### 1.2 Marseillais chess (the rule-restriction toolbox)
**Marseillais chess** (1920s, played by Alekhine and Réti): *both* players move twice
per turn. Its rules are the standard solutions to the awkward cases our axiom creates:

- **Check ends the turn**: if your first move gives check, you forfeit the second move.
  (A common sub-variant makes a first-move check simply illegal.)
- A player in check must resolve it on their **first** move of the turn.
- **En passant**: only the *last* double-step pawn move is capturable e.p. (some sources
  allow capturing either of two pawns pushed in one turn; we adopt "last half-move only"
  as the computationally clean reading).
- The original game was found to give the first player too big an advantage, producing
  **Balanced Marseillais** (White's first turn is a single move). Lesson: in double-move
  games, **first-move advantage is amplified** and must itself be treated as a parameter.

**Prior extracted**: the *check-ends-turn* rule is the canonical damper on double-move
mating power, and turn order is a live balance parameter, not a formality.

### 1.3 Progressive chess and handicap (odds) chess
**Progressive (Scotch) chess** — 1, 2, 3, … moves per turn, check ends a series —
demonstrates how quickly move-count superiority ends games: most Progressive games end
by mate delivered mid-series; defense consists of prophylaxis against *series mates*,
not against single moves. It is the extreme illustration that **threats scale with
moves-per-turn, parries don't**.

Classical **odds chess** calibrates material vs. tempo at the *small* end: "pawn and
move", "pawn and two moves", knight odds, queen odds. Historical practice treats "two
extra tempi at the start" as worth roughly a pawn-ish concession — but a **one-time**
tempo injection. Our axiom is a **perpetual tempo annuity**, which section 2 argues is
categorically different.

---

## 2. Theoretical analysis of the asymmetry

### 2.1 The tempo annuity does not amortize
Classical opening theory prices a tempo at roughly ⅓ pawn. A naive linearization of the
axiom — the double-mover nets +1 tempo per round — prices the asymmetry at +⅓ pawn per
round, i.e. **unbounded as the game lengthens**. So *no fixed material handicap can
balance the game asymptotically*; a material handicap only works if the single-mover can
**convert material into termination pressure** (mate threats, or forced simplification
into a position where extra moves don't help) faster than the annuity compounds.

This yields the central qualitative prediction:

> **P1 (Race structure).** Balanced two-move chess is a race: the single-mover's
> material advantage decays in usefulness over time, so balanced rulesets will show
> short decisive games, and rule changes that lengthen the game favor the double-mover.

### 2.2 The threat-parity inequality
Let T_d = independent threats the double-mover can create per turn (up to 2: two
half-moves, or one move creating a double threat), and P_s = threats the single-mover
can parry per turn (1, occasionally 2 with a single move that parries both). Threat
accumulation is roughly T_d − P_s ≥ 1 per turn in tactical positions. Any position
where the double-mover can keep generating *independent* threats is winning for them.
Defense for the single-mover is only possible in positions that are **prophylactically
saturated** — where most candidate threats are pre-parried (e.g., a compact full army
covering all near-king squares). This explains the Monster-chess material scheme from
first principles: the full orthodox army in its starting configuration is close to
prophylactically saturated; *that* is what one full army of material buys.

> **P2 (Saturation).** Removing "redundant defenders" from the single-mover hurts far
> more than its nominal pawn value; removing attackers from the double-mover hurts
> roughly linearly. Balance is therefore tuned most finely on the double-mover's side.

### 2.3 What two moves are worth by piece type
Two half-moves compose. For the double-mover each piece effectively becomes a
"squared" piece once per turn:

- **Knight²** reaches up to 2 king-steps' worth of L-jumps — covers the 5×5 box and
  smells like a short-range queen; knights gain the most.
- **Pawn²** advances two ranks a turn: a passed pawn promotes in ≤3 turns from its home
  square. **Pawn storms and promotion races are the double-mover's cheapest win
  condition** — highly relevant because our material schemes leave the double-mover
  pawn-rich.
- **King²** escapes almost any net (see Monster chess).
- **Queen²/Rook²** are devastating in open positions (relocate + strike in one turn ⇒
  unstoppable threats), which is why the double-mover's queen must be the first thing
  removed on the material ladder.

> **P3 (Ladder ordering).** The material ladder should be ordered by *double-move
> potency* (Q first, then R, then B, then N, then pawns), not by classical value.

### 2.4 Check regimes change the game class
Three coherent regimes for what "check" means inside a double turn:

- **R-KC (king-capture / Monster semantics)**: no check legality at all; win by
  capturing the king. Strongest for the double-mover (mate = any two-half-move capture
  path to the king; own king can transit attacked squares).
- **R-ET (Marseillais, check ends turn)**: each half-move individually legal; giving
  check on the first half-move immediately ends the turn. This *caps the mating throughput* of
  the double-mover: no "check + follow-up" combinations. Substantially tames §2.2.
- **R-IL (first-move check illegal)**: as R-ET but a first-half-move check is illegal
  rather than turn-ending. Slightly weaker for the double-mover than R-ET (loses even
  the option of a deliberate single-move turn via check) and simpler for search.

> **P4 (Regime ordering).** Double-mover strength: R-KC > R-ET > R-IL, with the
> R-KC gap large (it revives check+capture combinations) — so the balanced material
> point under R-ET/R-IL sits meaningfully *higher* on the ladder than Monster chess.

### 2.5 Second-move restrictions (fine-grained dampers)
- **NC2 (no capture on the second half-move)**: kills "approach + capture" and
  "capture + capture" turns; material can only be taken by a piece already in contact.
  Expected to be a *large* damper on the annuity's cash-out mechanism.
- **DP2 (second half-move must move a different piece)**: kills piece² effects from
  §2.3 (no N², no P² promotion sprints) while preserving two-threat turns; a *medium*
  damper with high strategic interest (turns the double move into "coordinate two
  pieces per turn").
- **Doubling period k**: double move only every k-th turn. k=∞ is standard chess; the
  annuity halves at k=2. A smooth, nearly continuous balance knob — the most useful
  *fine-tuning* parameter after material, though it costs some of the variant's identity.

### 2.6 Draw and termination theory
The single-mover's king can never outrun accumulated threats forever, and the
double-mover's king can rarely be mated (§1.1) — so **draws by insufficient mating
prospects are asymmetric**: a "drawish" rule mostly shelters the double-mover's king
while their pawns promote (§2.3). Predictions: draw rates will be low in unbalanced
rulesets and modest even near balance; a game-length cap adjudicated as a draw slightly
favors whoever is behind (usually the single-mover early, double-mover late).
Stalemate-of-the-single-mover becomes *more* common (their mobility is halved
relative to threats); we keep stalemate = draw and measure its frequency.

### 2.7 First-move advantage
Per §1.2, the side moving first in a double-move game gets amplified initiative. We
therefore measure every ruleset in both turn orders (double-mover first vs.
single-mover first) and treat turn order as a free half-parameter; "single-mover moves
first" is a costless concession available for fine-tuning.

---

## 3. Hypotheses to test empirically

- **H1 (No-restriction blowout)**: With full symmetric material and no rule dampers
  (any regime), the double-mover scores >95%. Material odds alone within "logical
  positions" cannot reach balance under R-KC without going below ~K+R-level armies.
- **H2 (Monster anchor)**: Under R-KC, balance crosses 50% somewhere in the
  K + 3–8 pawns band (Monster chess ±2 pawns), validating §1.1's folk assessment.
- **H3 (Regime lift)**: Under R-ET, the crossing moves up the ladder by roughly a
  rook-to-queen's worth of army (e.g., K+R+pawns or K+2 minors+pawns armies become
  competitive).
- **H4 (Damper stacking)**: R-ET + NC2 + DP2 stacked lifts the crossing to
  "full army minus queen minus rooks" territory or beyond — i.e., rule dampers can buy
  back most of the material gap while keeping both armies recognizable.
- **H5 (Race structure)**: Near-balanced rulesets have short decisive games
  (median < 35 full turns) and low draw rates (<20%).
- **H6 (Turn order)**: Giving the single-mover the first move is worth a measurable
  but small score shift (1–5 percentage points), usable for final trimming.

Each hypothesis maps to a sweep stage in `plan.md` §Sweep Design.

**Pilot verdicts (2026-07-09, 3000 nodes/half-move, 32 games/point — see
`experiments/results/REPORT.md`)**: H1 confirmed (72/72 all regimes). H2 *refuted* —
the KC ladder never crosses 50%; even K+3P scores 0.89, so king-capture semantics
appear unbalanceable by material alone. H3 confirmed in direction but the ET crossing
sits at **K+N+8P (0.562) / K+8P (0.531)**, far below the guessed band — the double
move is worth even more than §2 estimated. H5 confirmed (median 25–29 rounds at the
crossing, draws <10%). P3's knight-over-bishop potency confirmed dramatically
(K+2N+8P 0.969 vs K+2B+8P 0.781 at equal nominal value, a non-monotonicity in the
ladder). H4/H6 pending (S3/S5). All pending the 4× budget-sensitivity gate.

---

## 4. The ruleset parameter space (formal)

A **Ruleset** is the tuple:

| Parameter | Symbol | Domain | Default |
|---|---|---|---|
| Double-mover color | `double_color` | {white, black} | white |
| First player | `first_player` | {white, black} | white |
| Check regime | `check_regime` | {KC, ET, IL} | ET |
| No capture on 2nd half-move | `nc2` | bool | false |
| Distinct piece on 2nd half-move | `dp2` | bool | false |
| Doubling period | `k` | {1, 2, 3} | 1 |
| Material scheme | `material` | named schemes below | — |
| Move cap (full turns) | `cap` | int | 150 → draw |

**Material schemes** (double-mover's army; single-mover has the full orthodox army
unless noted; all placements on standard home squares, symmetric left/right where
possible — per FR-002):

| Name | Double-mover army | ~Pawns of material |
|---|---|---|
| `full` | full orthodox army | 40 |
| `no_q` | full minus queen | 30.5 |
| `no_q_r` | minus queen, one rook (a1) | 25.5 |
| `no_q_rr` | minus queen, both rooks (= K + 2N + 2B + 8P) | 20.5 |
| `bishops_pawns` | K + 2B + 8P | 14.5 |
| `knights_pawns` | K + 2N + 8P | 14 |
| `k_n_pawns` | K + N(b1) + 8P | 11 |
| `k_pawns8` | K + 8P | 8 |
| `k_pawns6` | K + 6P (b–g files) | 6 |
| `monster4` | K + 4P (c,d,e,f) — Monster chess | 4 |
| `k_pawns3` | K + 3P (d,e,f) | 3 |

The ladder is ordered by §2.3's potency principle: queen leaves first, then rooks, then
bishops before knights (knights² are the stronger double-move minors), then pawns
thin from the flanks inward (center pawns shield the king and are kept longest).

---

## 5. Why we must build our own engine

No existing strong engine can play this game:

- **Stockfish / Lc0**: hard-coded single-move alternation.
- **Fairy-Stockfish** exposes a rich variant configuration language (piece types, board
  sizes, win conditions) but its search and move generation assume **one move per turn**
  — multi-move variants (Marseillais, Progressive, Monster) are explicitly outside its
  framework. Same for Multi-Variant Stockfish forks.
- Generic GGP engines (e.g., Ludii) know Marseillais-family games but play far too
  weakly to give each ruleset "a fighting chance", and weak play systematically
  **overstates the double-mover's score** (defense is harder to play than attack here —
  a defender must see the double threat coming; an attacker just needs any two-move
  tactic). Engine strength is therefore not a nicety: *the balance point itself moves
  with engine strength*, and we must (a) use matched engines on both sides, and (b)
  check result stability across two node budgets before trusting a crossing (plan.md,
  validation gates).

Design consequences for the engine (implemented in `plan.md` §Engine):

1. Search the **half-move tree with a turn-schedule function** deciding side-to-move —
   minimax/alpha-beta is unaffected by consecutive same-player plies as long as
   max/min is chosen by *node owner*, not by depth parity.
2. **Fixed node budgets, not fixed depth**: the double-mover's turn has branching ~35²,
   the single-mover's ~35; equal depth would give wildly unequal thinking effort.
3. **Quiescence search matters more than in chess** — the horizon effect at a turn
   boundary is two half-moves deep; a "quiet" cutoff mid-turn is meaningless. Quiescence
   must respect the turn schedule.
4. Evaluation must price **threat exposure of the single-mover's king** and **passed
   pawns of the double-mover** above orthodox weights (§2.2, §2.3); a first version can
   use orthodox material+PST and rely on search, but this is the first upgrade lever.
5. Under R-KC, move legality is pseudo-legal (king capture allowed) — search is
   *simpler* and faster; under R-ET/IL we inherit python-chess legality per half-move.

---

## 6. Measurement theory

- **Score**: s = (W + D/2)/N for the double-mover; Wilson 95% CI on the underlying
  binomial (draws folded at half-weight via the normal approximation on score); also
  report Elo-equivalent `400·log10(s/(1−s))`.
- **Precision economics**: CI half-width ≈ 1.96·√(s(1−s)/N): ±10% needs ~96 games,
  ±5% needs ~384. Coarse ladder stages use N≈100/point; only near-crossing points get
  N≥300. A **bisection** on the (empirically monotone) material ladder concentrates
  games near the 50% crossing (validated by checking monotonicity across the full
  coarse sweep first).
- **Diversity**: identical deterministic engines would replay one game; we randomize
  among near-optimal root moves (softmax over root scores within a margin) for the
  first 8 full turns, seeded per game, and alternate turn order across the pair.
- **Confounds tracked**: engine-strength sensitivity (repeat crossing points at 2×
  budget — H-gate), draw-rate pathologies (§2.6), game-cap adjudications (report
  separately, sweep cap on suspicion).

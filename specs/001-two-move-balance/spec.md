# Feature Specification: Balancing Two-Move Chess

**Feature Branch**: `claude/two-move-chess-balance-mku5j2`
**Created**: 2026-07-09
**Status**: Active
**Input**: Given the foundational axiomatic rule — one player moves twice per turn, the
other moves once — find rulesets that balance the win rate between the two players under
good play.

## Overview

We study an asymmetric chess variant defined by a single axiom:

> **Axiom (Two-Move Asymmetry).** On each of their turns, the *double-mover* makes two
> successive half-moves; the *single-mover* makes one.

Everything else — starting material, check semantics, restrictions on the second
half-move, doubling frequency, turn order — is a **free parameter**. The goal of the
study is to locate points in this parameter space where the game is *balanced*: each
side wins close to 50% of decisive games under reasonably strong, symmetric play.

## User Scenarios & Testing

### Primary User Story
A variant designer wants a version of two-move chess that is fair enough to play
competitively. They consult this study's results to pick a ruleset (starting material +
rule modifiers) whose measured win rate is statistically indistinguishable from 50/50
(or within a stated tolerance band), with the constraint that the starting position
still "looks like chess" — pieces on sensible home squares, no visually arbitrary setup.

### Acceptance Scenarios
1. **Given** a candidate ruleset, **When** N self-play games are run between identical
   engines under that ruleset, **Then** the framework reports the double-mover's score
   with a 95% confidence interval, game-length statistics, and termination reasons.
2. **Given** a parameter sweep specification (material ladder × rule modifiers),
   **When** the sweep is executed, **Then** a ranked report identifies the ruleset(s)
   closest to 50% and the sensitivity of balance to each parameter.
3. **Given** the variant rules, **When** the engine plays, **Then** it never makes an
   illegal move under the configured ruleset (verified by rule unit tests and full-game
   legality audits).

### Edge Cases (rules must define behavior for all of these)
- Double-mover gives check on the **first** half-move (Marseillais: turn ends; or
  illegal; or irrelevant under king-capture semantics).
- Double-mover is **in check** at the start of their turn (must resolve on the first
  half-move under strict legality).
- Double-mover has a legal first half-move but **no legal second** half-move
  (turn ends after one move vs. stalemate — must be explicit).
- Single-mover is stalemated / double-mover is stalemated on first half-move.
- **En passant**: a double pawn push on the first half-move followed by another move —
  which e.p. rights survive to the opponent's turn?
- Repetition detection must include *within-turn* state (whose half-move it is).
- Pawn promotion on the first half-move followed by a second move with the promoted piece.

## Requirements

### Functional Requirements
- **FR-001**: The system MUST implement a configurable two-move chess ruleset with, at
  minimum, these sweepable parameters: starting material scheme, check regime,
  second-half-move capture restriction, distinct-piece restriction, doubling period,
  which color is the double-mover, and game-length cap.
- **FR-002**: Starting positions MUST remain "logical": pieces on the standard back-rank
  squares (subsets thereof), pawns on the 2nd/3rd rank, left-right sensible; no free-form
  scattering. Material handicaps are expressed as removals from (or standard additions
  to) the orthodox array.
- **FR-003**: The system MUST include a variant-aware engine that searches the actual
  game tree of the configured ruleset (i.e., understands that one side moves twice),
  strong enough to punish one-move blunders and exploit basic double-move tactics.
- **FR-004**: The system MUST run self-play matches between identical engine
  configurations with per-game opening diversification and report win/draw/loss counts.
- **FR-005**: The analysis MUST report score with Wilson 95% confidence intervals and an
  Elo-equivalent, per ruleset, and aggregate sweep results into a single report.
- **FR-006**: The framework MUST support staged sweeps (coarse material ladder →
  refinement near the 50% crossing → rule-modifier sweeps at the crossing).
- **FR-007**: Engine quality MUST be validated: ≥99% score vs. a random mover, and a
  strictly positive scaling result (2× node budget beats 1× budget) under the variant rules.
- **FR-008**: Every game record MUST be reproducible: ruleset, seed, node budget, and
  move list are logged.

### Key Entities
- **Ruleset**: complete parameterization of one game variant (see research.md §4).
- **MaterialScheme**: named starting-army pair, e.g. `monster4` (K+4P vs full army).
- **GameRecord**: ruleset id, seed, result, termination reason, move list.
- **SweepSpec**: list/grid of rulesets plus games-per-point and engine budget.

## Balance Criterion

A ruleset is **balanced at tolerance τ** if the double-mover's expected score
`s = (W + D/2) / N` satisfies `|s − 0.5| ≤ τ` with 95% confidence. Primary target:
τ = 0.05 (Elo gap ≲ 35). Draws count half; excessive draw rates (>60%) are flagged as a
separate playability concern.

## Out of Scope (this phase)
- Human playtesting; UI; opening theory beyond randomized diversification.
- Proving game-theoretic values; we measure empirical balance under matched engines.
- Non-chess boards, fairy pieces (the parameter space is already large).

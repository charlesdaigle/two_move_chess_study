//! Alpha-beta over the half-move tree. Port target: `twomove/engine.py:
//! SearchEngine`. Key properties to preserve for the differential test:
//!  - node budget per decision, NOT fixed depth (branching is ~b^2 on a double
//!    turn; equal depth would give unequal effort).
//!  - max/min chosen by node owner (turn schedule), no negamax sign flip inside
//!    a double turn. Scores always from White's perspective.
//!  - iterative deepening; TT keyed by (zobrist, half-index, owner, phase).
//!  - schedule-aware quiescence with "evasion" nodes: the mover may not stand pat
//!    while its king is en prise (KC) or in check (ET/IL).
//!  - seeded root-softmax over near-best moves for the first `soft_turns` turns
//!    (opening diversification) — must match Python's RNG stream for replay.
//!
//! Defaults from Python: nodes=3000 (pilot) / 12000 (confirm), soft_turns=8,
//! soft_margin=60, soft_temp=30.0, tt_max=400_000.

#[derive(Clone, Copy, Debug)]
pub struct SearchConfig {
    pub nodes: u64,
    pub soft_turns: u32,
    pub soft_margin: i32,
    pub soft_temp: f64,
    pub tt_max: usize,
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self { nodes: 3000, soft_turns: 8, soft_margin: 60, soft_temp: 30.0, tt_max: 400_000 }
    }
}

pub const MATE: i32 = 1_000_000;

// TODO(port): `choose(state, cfg, seed) -> HalfMove`.

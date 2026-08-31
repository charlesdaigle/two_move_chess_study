//! Turn schedule: the double-mover plays two successive half-moves, the
//! single-mover one. Port target: `twomove/rules.py: GameState`.
//!
//! Balanced order (research.md 1.2): first_player makes ONE half-move on turn 1,
//! then W / B B / W W / B B ...  Search maximizes by the mover of each node, so
//! consecutive same-owner plies never flip sign (engine.py already does this).
//!
//! Edge cases the port must cover (spec.md "Edge Cases"):
//!  - first half-move gives check  -> ET: turn ends; IL: that move is illegal.
//!  - in check at start of turn    -> must be resolved on the first half-move.
//!  - legal first, no legal second -> turn just ends (not stalemate).
//!  - en passant only against the immediately preceding half-move.
//!  - repetition key includes whose half-move it is + the doubling phase.

use crate::piece::Color;
use crate::rules::Ruleset;

/// Which side owns the half-move about to be played, and whether a second
/// half-move remains in the current turn.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Schedule {
    pub mover: Color,
    pub second_half_pending: bool,
}

impl Schedule {
    pub fn opening(rules: &Ruleset) -> Self {
        Self { mover: rules.first_player, second_half_pending: false }
    }
}

// TODO(port): `advance(...)`, `is_double_turn(turn_no)`, repetition key.

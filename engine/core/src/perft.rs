//! Perft: the correctness anchor for the movegen port.
//!
//! Two independent reference sets, both required to agree (plan T2 "done when"):
//!  1. ORTHODOX, regimes off: published perft tables to depth 6 — startpos,
//!     Kiwipete, and >=3 more standard positions.
//!  2. MARSEILLAIS (two-move turns, ET / IL): counted two independent ways —
//!     this Rust generator, and an instrumented run of `twomove/rules.py`
//!     (`GameState.legal_halfmoves` walked recursively). Must agree to depth 4.
//!
//! `perft` counts leaf *half-move sequences* for orthodox mode; for two-move
//! mode it counts leaf *turns* (see turn.rs). Keep the two entry points separate.

use crate::board::Board;

/// Orthodox half-move perft. TODO(port): implement once movegen exists.
pub fn perft_orthodox(_board: &Board, _depth: u32) -> u64 {
    0
}

#[cfg(test)]
mod tests {
    // Startpos reference (orthodox): 20, 400, 8902, 197281, 4865609, 119060324.
    // Enable once `perft_orthodox` is implemented.
    #[test]
    #[ignore = "movegen not yet ported"]
    fn startpos_depth_1() {
        // let b = super::Board::orthodox_start();
        // assert_eq!(super::perft_orthodox(&b, 1), 20);
    }
}

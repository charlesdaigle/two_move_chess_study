//! Half-move generation. THIS IS THE FIRST REAL PORT TASK (plan phase T2).
//!
//! Steps, in order:
//!   1. Orthodox pseudo-legal movegen on `Geometry(8,8)` — leapers (N, K),
//!      sliders (B, R, Q), pawns (push/double/capture/promotion/ep), castling.
//!   2. `perft` fixtures pass to depth 6 on startpos + Kiwipete + 3 more.
//!   3. Differential test vs python-chess on 10k random positions (regimes off).
//!   4. Generalize offsets to `Geometry(files, ranks)` and add a Betza descriptor
//!      table for fairy kinds.
//!   5. Legality filter per `CheckRegime` (KC = none, ET/IL = python-chess-style).
//!
//! Only after 1-3 reproduce the Python engine's move choices on the pilot corpus
//! do we touch eval (see README).

use crate::board::Board;

/// A half-move. `promotion` is `Some(kind)` for a promoting pawn push/capture.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HalfMove {
    pub from: u16,
    pub to: u16,
    pub promotion: Option<crate::piece::PieceKind>,
}

/// Pseudo-legal half-moves for the side to move. TODO(port): implement.
pub fn pseudo_legal(_board: &Board) -> Vec<HalfMove> {
    Vec::new()
}

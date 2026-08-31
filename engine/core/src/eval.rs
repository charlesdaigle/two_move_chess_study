//! Static evaluation, centipawns, White's perspective.
//!
//! FAITHFUL PORT FIRST. `twomove/engine.py: evaluate()` is exactly:
//!     material (PIECE_VALUES) + piece-square tables + a passed-pawn rank bonus.
//! No king safety, no mobility. Reproduce that, pass the differential test on the
//! pilot corpus, THEN add terms as separately-benchmarked changes (research.md
//! section 5 wants king-threat exposure + passed-pawn urgency; both matter more
//! under the two-move axiom).
//!
//! PSTs are 8x8 in the Python version. For larger boards the port needs a
//! geometry-aware scheme (centre-distance formula) — decide when Phase 03 lands.

use crate::board::Board;

/// TODO(port): material + PST + passed-pawn bonus, byte-for-byte with Python.
pub fn evaluate(_board: &Board) -> i32 {
    0
}

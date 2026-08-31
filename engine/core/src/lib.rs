//! twomove-core — the Rust rules kernel + engine for the two-move chess study.
//!
//! Port target: `twomove/rules.py` + `twomove/engine.py` (Python, python-chess).
//! The Rust version exists to (a) run fast enough for the expanded search space
//! and (b) support parameterized boards up to 12x12 and Betza fairy pieces, which
//! python-chess cannot represent.
//!
//! Port discipline (see engine/README.md): reproduce the Python engine's move
//! choices on the committed pilot corpus *before* adding king-safety / mobility
//! eval terms. The Python engine is the differential-test oracle.

pub mod geometry;
pub mod piece;
pub mod board;
pub mod rules;
pub mod movegen;
pub mod turn;
pub mod eval;
pub mod search;
pub mod perft;

pub use geometry::{Geometry, Square};
pub use piece::{Color, Piece, PieceKind};
pub use board::Board;

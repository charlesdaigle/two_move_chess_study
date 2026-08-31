//! Mailbox board: `geometry.count()` slots of `Option<Piece>`, plus side to move
//! and the state a two-move turn needs. This is deliberately a plain array, not
//! bitboards — 144 squares and fairy movers make bitboards more trouble than
//! they are worth here, and search cost is dominated by the turn tree anyway.

use crate::geometry::{Geometry, Square};
use crate::piece::{Color, Piece, PieceKind};

#[derive(Clone, Debug)]
pub struct Board {
    pub geom: Geometry,
    squares: Vec<Option<Piece>>,
    pub side_to_move: Color,
    /// En-passant target square, set only by the immediately preceding half-move
    /// (matches the Python "last half-move only" reading).
    pub ep_target: Option<Square>,
    // TODO(port): castling rights keyed by (color, side), tracked per material
    //   scheme like twomove/rules.py: rooks that don't start on home squares
    //   grant no rights.
}

impl Board {
    pub fn empty(geom: Geometry) -> Self {
        Self {
            geom,
            squares: vec![None; geom.count()],
            side_to_move: Color::White,
            ep_target: None,
        }
    }

    #[inline]
    pub fn at(&self, sq: Square) -> Option<Piece> {
        self.squares[sq as usize]
    }

    #[inline]
    pub fn set(&mut self, sq: Square, piece: Option<Piece>) {
        self.squares[sq as usize] = piece;
    }

    pub fn king_square(&self, color: Color) -> Option<Square> {
        self.squares.iter().position(|p| {
            matches!(p, Some(Piece { color: c, kind: PieceKind::King }) if *c == color)
        }).map(|i| i as Square)
    }

    /// Orthodox 8x8 starting position. The study's non-`full` armies are this
    /// minus removals (see `twomove/rules.py: MATERIAL_SCHEMES`); those get built
    /// on top once the scheme loader is ported.
    pub fn orthodox_start() -> Self {
        let geom = Geometry::new(8, 8);
        let mut b = Board::empty(geom);
        use PieceKind::*;
        let back = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook];
        for (file, &kind) in back.iter().enumerate() {
            let f = file as u8;
            b.set(geom.square(f, 0), Some(Piece::new(Color::White, kind)));
            b.set(geom.square(f, 1), Some(Piece::new(Color::White, Pawn)));
            b.set(geom.square(f, 7), Some(Piece::new(Color::Black, kind)));
            b.set(geom.square(f, 6), Some(Piece::new(Color::Black, Pawn)));
        }
        b
    }

    pub fn piece_count(&self) -> usize {
        self.squares.iter().filter(|p| p.is_some()).count()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn startpos_shape() {
        let b = Board::orthodox_start();
        assert_eq!(b.piece_count(), 32);
        assert_eq!(b.side_to_move, Color::White);
        assert_eq!(
            b.at(b.geom.square(4, 0)),
            Some(Piece::new(Color::White, PieceKind::King))
        );
        assert_eq!(b.king_square(Color::Black), Some(b.geom.square(4, 7)));
    }
}

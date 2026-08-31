//! Piece kinds. Orthodox set first; fairy kinds get added here with a Betza
//! descriptor table in `movegen` (Phase 03 of the plan). Keep the orthodox
//! discriminants stable — perft fixtures and the Python oracle depend on them.

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum Color {
    White = 0,
    Black = 1,
}

impl Color {
    #[inline]
    pub const fn flip(self) -> Color {
        match self {
            Color::White => Color::Black,
            Color::Black => Color::White,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum PieceKind {
    Pawn = 0,
    Knight = 1,
    Bishop = 2,
    Rook = 3,
    Queen = 4,
    King = 5,
    // Fairy kinds land here (Phase 03). Discriminants >= 6 reserved.
}

impl PieceKind {
    /// Centipawn base value used by the ported eval. Matches
    /// `twomove/engine.py: PIECE_VALUES` exactly — do not "improve" during the
    /// faithful port.
    pub const fn base_value(self) -> i32 {
        match self {
            PieceKind::Pawn => 100,
            PieceKind::Knight => 320,
            PieceKind::Bishop => 330,
            PieceKind::Rook => 500,
            PieceKind::Queen => 950,
            PieceKind::King => 0,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Piece {
    pub color: Color,
    pub kind: PieceKind,
}

impl Piece {
    pub const fn new(color: Color, kind: PieceKind) -> Self {
        Self { color, kind }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn values_match_python_oracle() {
        assert_eq!(PieceKind::Queen.base_value(), 950);
        assert_eq!(PieceKind::King.base_value(), 0);
    }

    #[test]
    fn color_flips() {
        assert_eq!(Color::White.flip(), Color::Black);
        assert_eq!(Color::Black.flip().flip(), Color::Black);
    }
}

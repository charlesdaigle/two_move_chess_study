//! Parameterized board geometry. Orthodox chess is `Geometry::new(8, 8)`.
//! Ceiling for the study is 12x12 (see the plan); nothing here hard-codes 8.

/// A square is a 0-based index into a `files * ranks` mailbox, `rank * files + file`.
/// `a1` == 0. Off-board is represented by `Option<Square>` at call sites, not a
/// sentinel value.
pub type Square = u16;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Geometry {
    pub files: u8,
    pub ranks: u8,
}

impl Geometry {
    pub const fn new(files: u8, ranks: u8) -> Self {
        assert!(files >= 2 && ranks >= 2, "board too small");
        assert!(files <= 12 && ranks <= 12, "board exceeds the 12x12 study ceiling");
        Self { files, ranks }
    }

    #[inline]
    pub const fn count(&self) -> usize {
        self.files as usize * self.ranks as usize
    }

    #[inline]
    pub const fn square(&self, file: u8, rank: u8) -> Square {
        (rank as u16) * (self.files as u16) + (file as u16)
    }

    #[inline]
    pub const fn file_of(&self, sq: Square) -> u8 {
        (sq % self.files as u16) as u8
    }

    #[inline]
    pub const fn rank_of(&self, sq: Square) -> u8 {
        (sq / self.files as u16) as u8
    }

    #[inline]
    pub fn on_board(&self, file: i16, rank: i16) -> Option<Square> {
        if file >= 0 && rank >= 0 && file < self.files as i16 && rank < self.ranks as i16 {
            Some(self.square(file as u8, rank as u8))
        } else {
            None
        }
    }

    /// Offset a square by (df, dr); `None` if it leaves the board.
    #[inline]
    pub fn offset(&self, sq: Square, df: i16, dr: i16) -> Option<Square> {
        self.on_board(self.file_of(sq) as i16 + df, self.rank_of(sq) as i16 + dr)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn orthodox_indices() {
        let g = Geometry::new(8, 8);
        assert_eq!(g.count(), 64);
        assert_eq!(g.square(0, 0), 0); // a1
        assert_eq!(g.square(7, 7), 63); // h8
        assert_eq!(g.file_of(63), 7);
        assert_eq!(g.rank_of(63), 7);
        assert_eq!(g.offset(0, 1, 0), Some(1)); // a1 -> b1
        assert_eq!(g.offset(0, -1, 0), None); // off the a-file
        assert_eq!(g.offset(63, 1, 1), None); // off h8
    }

    #[test]
    fn big_board() {
        let g = Geometry::new(12, 12);
        assert_eq!(g.count(), 144);
        assert_eq!(g.rank_of(g.square(3, 11)), 11);
    }
}

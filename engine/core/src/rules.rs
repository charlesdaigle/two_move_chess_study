//! Ruleset parameters. Direct port target: `twomove/rules.py: Ruleset` +
//! `research.md` section 4. KC is kept only as a control (see the plan); ET and
//! IL are the studied regimes.

use crate::piece::Color;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CheckRegime {
    /// King-capture (Monster semantics): half-moves pseudo-legal, win by taking
    /// the king. Control / boundary case only.
    Kc,
    /// Marseillais: each half-move fully legal; a first half-move that gives
    /// check ends the turn. The load-bearing damper.
    Et,
    /// As ET but a first half-move that gives check is illegal, not turn-ending.
    Il,
}

#[derive(Clone, Debug)]
pub struct Ruleset {
    pub double_color: Color,
    pub first_player: Color,
    pub check_regime: CheckRegime,
    /// No capture on the second half-move.
    pub nc2: bool,
    /// Second half-move must move a different piece.
    pub dp2: bool,
    /// Doubling period: the double-mover doubles only every k-th turn (k=1 = always).
    pub k: u8,
    /// Draw after this many full turns.
    pub cap: u32,
    // material scheme name is resolved by the scheme loader (Phase 03 port).
}

impl Default for Ruleset {
    fn default() -> Self {
        Self {
            double_color: Color::White,
            first_player: Color::White,
            check_regime: CheckRegime::Et,
            nc2: false,
            dp2: false,
            k: 1,
            cap: 150,
        }
    }
}

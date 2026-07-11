"""Rules kernel for two-move chess.

The axiom: the *double-mover* makes two successive half-moves per turn, the
*single-mover* makes one. Everything else is a Ruleset parameter (see
specs/001-two-move-balance/research.md section 4).

Check regimes:
  KC  king-capture (Monster chess semantics): half-moves are pseudo-legal, check is
      not enforced, the game is won by capturing the enemy king. Castling still obeys
      orthodox constraints (not out of/through check).
  ET  Marseillais: each half-move is fully legal; a first half-move that gives check
      ends the turn immediately (the second half-move is forfeited).
  IL  as ET, but a first half-move that gives check is illegal instead of turn-ending.

En passant: only the pawn that made a double step on the *last* half-move may be
captured en passant (implemented naturally by the internal null-move turn flip).

Repetition: threefold repetition of a full-turn-boundary state (position + player to
move + doubling phase) is a draw. No-progress: 100 half-moves without a capture or
pawn move is a draw. Move cap: `cap` full turns, then draw.
"""

from __future__ import annotations

import dataclasses
from typing import Dict, List, Optional, Tuple

import chess

WHITE, BLACK = chess.WHITE, chess.BLACK

KC, ET, IL = "KC", "ET", "IL"

# --- Material schemes -------------------------------------------------------
# Maps scheme name -> white-army piece placement (square -> piece symbol).
# The single-mover always gets the full orthodox army; the double-mover gets the
# scheme army. Placements stay on standard home squares (spec FR-002).

_FULL_BACK = {"a1": "R", "b1": "N", "c1": "B", "d1": "Q", "e1": "K", "f1": "B", "g1": "N", "h1": "R"}
_PAWNS = {f + "2": "P" for f in "abcdefgh"}


def _army(back_keep: str, pawn_files: str) -> Dict[str, str]:
    army = {sq: p for sq, p in _FULL_BACK.items() if p in back_keep or p == "K"}
    army.update({f + "2": "P" for f in pawn_files})
    return army


MATERIAL_SCHEMES: Dict[str, Dict[str, str]] = {
    "full": {**_FULL_BACK, **_PAWNS},
    "no_q": {**{sq: p for sq, p in _FULL_BACK.items() if p != "Q"}, **_PAWNS},
    "no_q_r": {**{sq: p for sq, p in _FULL_BACK.items() if p != "Q" and sq != "a1"}, **_PAWNS},
    "no_q_rr": _army("NB", "abcdefgh"),
    "bishops_pawns": _army("B", "abcdefgh"),
    "knights_pawns": _army("N", "abcdefgh"),
    "k_n_pawns": {**{"b1": "N", "e1": "K"}, **_PAWNS},
    "k_pawns8": _army("", "abcdefgh"),
    "k_pawns6": _army("", "bcdefg"),
    "monster4": _army("", "cdef"),
    "k_pawns3": _army("", "def"),
    # Interpolation rungs for ladder bisection near the ET crossing
    # (strategy.md); pawns thin flank-inward to stay "logical".
    "k_r_pawns": {**{"a1": "R", "e1": "K"}, **_PAWNS},
    "k_b_pawns": {**{"c1": "B", "e1": "K"}, **_PAWNS},
    "k_n_pawns7": {**{"b1": "N", "e1": "K"}, **{f + "2": "P" for f in "bcdefgh"}},
    "k_pawns7": _army("", "bcdefgh"),
    "k_pawns5": _army("", "cdefg"),
}

# Ladder ordered by double-move potency (research.md P3), strongest first.
LADDER = [
    "full", "no_q", "no_q_r", "no_q_rr", "bishops_pawns", "knights_pawns",
    "k_n_pawns", "k_pawns8", "k_pawns6", "monster4", "k_pawns3",
]


@dataclasses.dataclass(frozen=True)
class Ruleset:
    material: str = "full"        # double-mover's army scheme
    check_regime: str = ET        # KC | ET | IL
    nc2: bool = False             # no captures on the second half-move
    dp2: bool = False             # second half-move must move a different piece
    k: int = 1                    # double move on the double-mover's 1st, (1+k)th, ... turn
    double_color: bool = WHITE    # which color is the double-mover
    first_player: bool = WHITE    # who moves first
    cap: int = 150                # full turns before draw adjudication

    def __post_init__(self):
        if self.material not in MATERIAL_SCHEMES:
            raise ValueError(f"unknown material scheme {self.material!r}")
        if self.check_regime not in (KC, ET, IL):
            raise ValueError(f"unknown check regime {self.check_regime!r}")
        if self.k < 1:
            raise ValueError("k must be >= 1")

    @property
    def rid(self) -> str:
        return (f"mat={self.material}|reg={self.check_regime}|nc2={int(self.nc2)}"
                f"|dp2={int(self.dp2)}|k={self.k}"
                f"|dbl={'W' if self.double_color else 'B'}"
                f"|first={'W' if self.first_player else 'B'}")

    def start_fen(self) -> str:
        board = chess.Board(None)
        scheme = MATERIAL_SCHEMES[self.material]
        full = MATERIAL_SCHEMES["full"]
        white_army = scheme if self.double_color == WHITE else full
        black_army = full if self.double_color == WHITE else scheme
        for sq, sym in white_army.items():
            board.set_piece_at(chess.parse_square(sq), chess.Piece.from_symbol(sym))
        for sq, sym in black_army.items():
            board.set_piece_at(chess.square_mirror(chess.parse_square(sq)),
                               chess.Piece.from_symbol(sym.lower()))
        board.turn = self.first_player
        castling = ""
        if board.piece_at(chess.E1) == chess.Piece.from_symbol("K"):
            if board.piece_at(chess.H1) == chess.Piece.from_symbol("R"):
                castling += "K"
            if board.piece_at(chess.A1) == chess.Piece.from_symbol("R"):
                castling += "Q"
        if board.piece_at(chess.E8) == chess.Piece.from_symbol("k"):
            if board.piece_at(chess.H8) == chess.Piece.from_symbol("r"):
                castling += "k"
            if board.piece_at(chess.A8) == chess.Piece.from_symbol("r"):
                castling += "q"
        board.set_castling_fen(castling or "-")
        return board.fen()


@dataclasses.dataclass(frozen=True)
class Outcome:
    winner: Optional[bool]   # WHITE, BLACK, or None for draw
    reason: str              # king_capture|checkmate|stalemate|repetition|no_progress|cap

    @property
    def result_str(self) -> str:
        if self.winner is None:
            return "1/2-1/2"
        return "1-0" if self.winner == WHITE else "0-1"


_NO_PROGRESS_LIMIT = 100  # half-moves without capture/pawn move


class GameState:
    """Mutable two-move-chess position with push/pop suitable for tree search."""

    def __init__(self, ruleset: Ruleset):
        self.rules = ruleset
        self.board = chess.Board(ruleset.start_fen())
        self.mover: bool = ruleset.first_player
        self.half_index: int = 0          # 0 = first half-move of the turn, 1 = second
        self.turn_no: Dict[bool, int] = {WHITE: 0, BLACK: 0}  # completed+current, per player
        self.turn_no[self.mover] = 1
        self.turns_played: int = 0        # completed full turns (both players)
        self.first_move_to: Optional[int] = None  # to-square of first half-move (for dp2)
        self.no_progress: int = 0
        self._king_captured: Optional[bool] = None  # color of the captured king
        self._rep: Dict[Tuple, int] = {}
        self._rep_draw = False
        self._undo: List[Tuple] = []
        self._legal_cache: Optional[List[chess.Move]] = None
        self._bump_repetition(+1)

    # -- turn schedule --------------------------------------------------------

    def is_double_turn(self) -> bool:
        return (self.mover == self.rules.double_color
                and (self.turn_no[self.mover] - 1) % self.rules.k == 0)

    # -- repetition -----------------------------------------------------------

    def _rep_key(self) -> Tuple:
        # Turn-boundary state: position (incl. side to move, castling, ep) plus the
        # doubling phase of each player's turn counter.
        phase = (self.turn_no[self.rules.double_color] - 1) % self.rules.k
        return (self.board._transposition_key(), self.mover, phase)

    def _bump_repetition(self, delta: int) -> None:
        key = self._rep_key()
        n = self._rep.get(key, 0) + delta
        if n:
            self._rep[key] = n
        else:
            self._rep.pop(key, None)
        if delta > 0 and n >= 3:
            self._rep_draw = True

    # -- legality -------------------------------------------------------------

    def legal_halfmoves(self) -> List[chess.Move]:
        if self._legal_cache is None:
            self._legal_cache = self._gen_legal()
        return self._legal_cache

    def _gen_legal(self) -> List[chess.Move]:
        if self.outcome_fast() is not None:
            return []
        board = self.board
        assert board.turn == self.mover
        if self.rules.check_regime == KC:
            # Pseudo-legal: check is not enforced. python-chess castling generation
            # already applies orthodox castling constraints even pseudo-legally.
            moves = list(board.pseudo_legal_moves)
        else:
            moves = list(board.legal_moves)
            if self.rules.check_regime == IL and self.half_index == 0 and self.is_double_turn():
                moves = [m for m in moves if not board.gives_check(m)]
        if self.half_index == 1:
            if self.rules.nc2:
                moves = [m for m in moves if not board.is_capture(m)]
            if self.rules.dp2 and self.first_move_to is not None:
                moves = [m for m in moves if m.from_square != self.first_move_to]
        return moves

    # -- termination ----------------------------------------------------------

    def outcome_fast(self) -> Optional[Outcome]:
        """Terminal conditions that need no move generation."""
        if self._king_captured is not None:
            return Outcome(winner=not self._king_captured, reason="king_capture")
        if self._rep_draw:
            return Outcome(winner=None, reason="repetition")
        if self.no_progress >= _NO_PROGRESS_LIMIT:
            return Outcome(winner=None, reason="no_progress")
        if self.turns_played >= 2 * self.rules.cap:
            return Outcome(winner=None, reason="cap")
        return None

    def outcome(self) -> Optional[Outcome]:
        fast = self.outcome_fast()
        if fast is not None:
            return fast
        if not self.legal_halfmoves():
            # No first half-move available (a dry second half-move just passes and is
            # handled inside push(), so half_index is always 0 here).
            if self.rules.check_regime != KC and self.board.is_check():
                return Outcome(winner=not self.mover, reason="checkmate")
            return Outcome(winner=None, reason="stalemate")
        return None

    # -- push / pop -----------------------------------------------------------

    def push(self, move: chess.Move) -> None:
        board = self.board
        undo = (self.mover, self.half_index, dict(self.turn_no), self.turns_played,
                self.first_move_to, self.no_progress, self._king_captured,
                self._rep_draw, self._legal_cache)
        mover = self.mover
        is_double = self.is_double_turn()
        captured = board.piece_at(move.to_square)
        is_cap = board.is_capture(move)  # includes en passant
        is_pawn = board.piece_type_at(move.from_square) == chess.PAWN
        gives_check = (self.rules.check_regime == ET and is_double
                       and self.half_index == 0 and board.gives_check(move))
        board.push(move)
        board_pushes = 1
        rep_bumped = False

        self.no_progress = 0 if (is_cap or is_pawn) else self.no_progress + 1
        if captured is not None and captured.piece_type == chess.KING:
            self._king_captured = captured.color

        turn_continues = (is_double and self.half_index == 0 and not gives_check
                          and self._king_captured is None)
        if turn_continues:
            board.push(chess.Move.null())   # back to the mover for the second half-move
            board_pushes += 1
            self.half_index = 1
            self.first_move_to = move.to_square
            self._legal_cache = None
            second = self._gen_legal()
            if second:
                self._legal_cache = second
            else:
                # no legal second half-move: the turn simply ends
                board.pop()                 # undo the null; opponent to move
                board_pushes -= 1
                self.half_index = 0
                self.first_move_to = None
                turn_continues = False

        if not turn_continues:
            # the turn is over: hand over to the opponent
            self.turns_played += 1
            self.half_index = 0
            self.first_move_to = None
            self.mover = not mover
            self.turn_no[self.mover] += 1
            self._legal_cache = None
            if self._king_captured is None:
                self._bump_repetition(+1)
                rep_bumped = True

        self._undo.append((undo, board_pushes, rep_bumped))

    def pop(self) -> None:
        undo, board_pushes, rep_bumped = self._undo.pop()
        if rep_bumped:
            self._bump_repetition(-1)
        for _ in range(board_pushes):
            self.board.pop()
        (self.mover, self.half_index, self.turn_no, self.turns_played,
         self.first_move_to, self.no_progress, self._king_captured,
         self._rep_draw, self._legal_cache) = undo

    # -- misc -----------------------------------------------------------------

    def tt_key(self) -> Tuple:
        extra = self.first_move_to if (self.rules.dp2 and self.half_index == 1) else -1
        return (self.board._transposition_key(), self.mover, self.half_index,
                self.is_double_turn(), extra)

    def fen(self) -> str:
        return self.board.fen()

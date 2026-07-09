"""Variant-aware engines for two-move chess.

SearchEngine: iterative-deepening alpha-beta over the *half-move* tree. The side to
maximize at each node is the node's mover (which the GameState turn schedule provides),
so consecutive same-player plies inside a double turn are handled naturally — no
negamax sign flip between them. Scores are always from White's perspective.

Budgets are in *nodes per half-move decision*, not depth: the double-mover's turns
have ~35^2 branching and equal depth would give wildly unequal effort (research.md §5).
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Tuple

import chess

from .rules import KC, WHITE, GameState

MATE = 1_000_000
INF = 10 * MATE

PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 950, chess.KING: 0,
}

# Compact piece-square tables (white perspective, a1=0), orthodox midgame flavor.
_PST_PAWN = [
      0,   0,   0,   0,   0,   0,   0,   0,
      5,  10,  10, -20, -20,  10,  10,   5,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,   5,  10,  25,  25,  10,   5,   5,
     10,  10,  20,  30,  30,  20,  10,  10,
     50,  50,  50,  50,  50,  50,  50,  50,
      0,   0,   0,   0,   0,   0,   0,   0,
]
_PST_KNIGHT = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]
_PST_BISHOP = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]
_PST_ROOK = [
      0,   0,   0,   5,   5,   0,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0,
]
_PST_QUEEN = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -10,   5,   5,   5,   5,   5,   0, -10,
      0,   0,   5,   5,   5,   5,   0,  -5,
     -5,   0,   5,   5,   5,   5,   0,  -5,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20,
]
_PST_KING = [
     20,  30,  10,   0,   0,  10,  30,  20,
     20,  20,   0,   0,   0,   0,  20,  20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
]
PST = {
    chess.PAWN: _PST_PAWN, chess.KNIGHT: _PST_KNIGHT, chess.BISHOP: _PST_BISHOP,
    chess.ROOK: _PST_ROOK, chess.QUEEN: _PST_QUEEN, chess.KING: _PST_KING,
}
# Passed-pawn bonus by rank (white perspective): promotion urgency matters extra in
# this variant (pawn advances two ranks per turn for the double-mover).
_PASSED = [0, 10, 15, 25, 40, 70, 120, 0]


def evaluate(board: chess.Board) -> int:
    """Static eval in centipawns from White's perspective."""
    score = 0
    pawns_w = board.pieces_mask(chess.PAWN, chess.WHITE)
    pawns_b = board.pieces_mask(chess.PAWN, chess.BLACK)
    for sq, piece in board.piece_map().items():
        pt = piece.piece_type
        if piece.color == chess.WHITE:
            v = PIECE_VALUES[pt] + PST[pt][sq]
            if pt == chess.PAWN and not _blockers_ahead(sq, pawns_b, chess.WHITE):
                v += _PASSED[chess.square_rank(sq)]
            score += v
        else:
            v = PIECE_VALUES[pt] + PST[pt][chess.square_mirror(sq)]
            if pt == chess.PAWN and not _blockers_ahead(sq, pawns_w, chess.BLACK):
                v += _PASSED[7 - chess.square_rank(sq)]
            score -= v
    return score


def _blockers_ahead(sq: int, enemy_pawns: int, color: bool) -> int:
    """Enemy pawns on this or adjacent files, ahead of sq (cheap passed-pawn test)."""
    f, r = chess.square_file(sq), chess.square_rank(sq)
    files = chess.BB_FILES[f]
    if f > 0:
        files |= chess.BB_FILES[f - 1]
    if f < 7:
        files |= chess.BB_FILES[f + 1]
    if color == chess.WHITE:
        ahead = ~0 << (8 * (r + 1))
    else:
        ahead = (1 << (8 * r)) - 1
    return enemy_pawns & files & ahead


class _Budget(Exception):
    pass


class SearchEngine:
    """Alpha-beta over the half-move tree with fixed node budget per decision."""

    name = "search"

    def __init__(self, nodes: int = 3000, seed: Optional[int] = None,
                 soft_turns: int = 8, soft_margin: int = 60, soft_temp: float = 30.0,
                 max_depth: int = 32, tt_max: int = 400_000):
        self.nodes_budget = nodes
        self.rng = random.Random(seed)
        self.soft_turns = soft_turns          # full rounds with randomized root choice
        self.soft_margin = soft_margin        # cp window eligible for randomization
        self.soft_temp = soft_temp
        self.max_depth = max_depth
        self.tt_max = tt_max
        self.tt: Dict[Tuple, Tuple] = {}
        self.nodes = 0

    # -- public ---------------------------------------------------------------

    def choose(self, state: GameState) -> chess.Move:
        moves = state.legal_halfmoves()
        if not moves:
            raise ValueError("no legal half-moves")
        if len(moves) == 1:
            return moves[0]
        self.nodes = 0
        if len(self.tt) > self.tt_max:
            self.tt.clear()
        root_scores: Dict[chess.Move, int] = {m: 0 for m in moves}
        best_move = moves[0]
        try:
            for depth in range(1, self.max_depth + 1):
                scores = self._search_root(state, moves, depth)
                root_scores = scores
                best_move = max(scores, key=lambda m: self._oriented(scores[m], state))
                # order for the next iteration: best first
                moves.sort(key=lambda m: -self._oriented(scores[m], state))
                if abs(root_scores[best_move]) > MATE // 2:
                    break
        except _Budget:
            pass
        return self._pick(state, root_scores, best_move)

    # -- root -----------------------------------------------------------------

    def _oriented(self, score: int, state: GameState) -> int:
        return score if state.mover == WHITE else -score

    def _search_root(self, state: GameState, moves: List[chess.Move],
                     depth: int) -> Dict[chess.Move, int]:
        scores: Dict[chess.Move, int] = {}
        maximizing = state.mover == WHITE
        alpha, beta = -INF, INF
        for m in moves:
            state.push(m)
            try:
                s = self._ab(state, depth - 1, alpha, beta, ply=1)
            finally:
                state.pop()
            scores[m] = s
            if maximizing:
                alpha = max(alpha, s)
            else:
                beta = min(beta, s)
        return scores

    def _pick(self, state: GameState, scores: Dict[chess.Move, int],
              best_move: chess.Move) -> chess.Move:
        """Softmax among near-best root moves during the opening phase."""
        in_opening = state.turn_no[state.mover] <= self.soft_turns
        if not in_opening or abs(scores[best_move]) > MATE // 2:
            return best_move
        best = self._oriented(scores[best_move], state)
        cands = [(m, self._oriented(s, state)) for m, s in scores.items()
                 if best - self._oriented(s, state) <= self.soft_margin]
        if len(cands) <= 1:
            return best_move
        weights = [math.exp((s - best) / self.soft_temp) for _, s in cands]
        return self.rng.choices([m for m, _ in cands], weights=weights, k=1)[0]

    # -- tree -----------------------------------------------------------------

    def _ab(self, state: GameState, depth: int, alpha: int, beta: int, ply: int) -> int:
        self.nodes += 1
        if self.nodes > self.nodes_budget:
            raise _Budget()
        out = state.outcome_fast()
        if out is None and not state.legal_halfmoves():
            out = state.outcome()
        if out is not None:
            if out.winner is None:
                return 0
            return (MATE - ply) if out.winner == WHITE else -(MATE - ply)
        if depth <= 0:
            return self._quiesce(state, alpha, beta, ply, qdepth=8)

        key = state.tt_key()
        tt_hit = self.tt.get(key)
        tt_move = None
        if tt_hit is not None:
            tt_depth, tt_flag, tt_score, tt_move = tt_hit
            if tt_depth >= depth and abs(tt_score) < MATE // 2:
                if tt_flag == 0:
                    return tt_score
                if tt_flag == -1 and tt_score <= alpha:
                    return tt_score
                if tt_flag == 1 and tt_score >= beta:
                    return tt_score

        moves = self._ordered(state, tt_move)
        maximizing = state.mover == WHITE
        best = -INF if maximizing else INF
        best_move = None
        a, b = alpha, beta
        for m in moves:
            state.push(m)
            try:
                s = self._ab(state, depth - 1, a, b, ply + 1)
            finally:
                state.pop()
            if maximizing:
                if s > best:
                    best, best_move = s, m
                a = max(a, s)
            else:
                if s < best:
                    best, best_move = s, m
                b = min(b, s)
            if a >= b:
                break
        flag = 0
        if best <= alpha:
            flag = -1
        elif best >= beta:
            flag = 1
        # Mate scores are ply-relative; keep the move for ordering but never let the
        # stored score produce a cutoff (depth -1).
        store_depth = depth if abs(best) < MATE // 2 else -1
        self.tt[key] = (store_depth, flag, best, best_move)
        return best

    def _quiesce(self, state: GameState, alpha: int, beta: int, ply: int,
                 qdepth: int) -> int:
        self.nodes += 1
        if self.nodes > self.nodes_budget:
            raise _Budget()
        out = state.outcome_fast()
        if out is not None:
            if out.winner is None:
                return 0
            return (MATE - ply) if out.winner == WHITE else -(MATE - ply)
        board = state.board
        mover = state.mover
        # "Evasion" nodes may not stand pat: doing nothing is not an option when the
        # mover's king is en prise (KC) or the mover is in check (ET/IL). Without
        # this the engine happily hangs its king behind the quiescence horizon.
        if state.rules.check_regime == KC:
            ksq = board.king(mover)
            evasion = ksq is not None and board.is_attacked_by(not mover, ksq)
        else:
            evasion = board.is_check()
        stand = evaluate(board)
        if qdepth <= 0:
            return stand
        maximizing = mover == WHITE
        if evasion:
            moves = list(state.legal_halfmoves())
            if not moves:
                if state.rules.check_regime != KC:  # mated
                    return -(MATE - ply) if maximizing else (MATE - ply)
                return 0
            best = -INF if maximizing else INF
        else:
            if maximizing:
                if stand >= beta:
                    return stand
                alpha = max(alpha, stand)
            else:
                if stand <= alpha:
                    return stand
                beta = min(beta, stand)
            moves = [m for m in state.legal_halfmoves() if board.is_capture(m)]
            best = stand
        moves.sort(key=lambda m: -self._mvv_lva(board, m))
        for m in moves:
            state.push(m)
            try:
                s = self._quiesce(state, alpha, beta, ply + 1, qdepth - 1)
            finally:
                state.pop()
            if maximizing:
                best = max(best, s)
                alpha = max(alpha, s)
            else:
                best = min(best, s)
                beta = min(beta, s)
            if alpha >= beta:
                break
        return best

    # -- helpers ---------------------------------------------------------------

    _VICTIM = {**PIECE_VALUES, chess.KING: 20_000}  # king capture ordered first (KC)

    @classmethod
    def _mvv_lva(cls, board: chess.Board, m: chess.Move) -> int:
        victim = board.piece_type_at(m.to_square)
        if victim is None:  # en passant
            victim = chess.PAWN
        attacker = board.piece_type_at(m.from_square) or chess.PAWN
        return cls._VICTIM[victim] * 10 - PIECE_VALUES[attacker]

    def _ordered(self, state: GameState, tt_move) -> List[chess.Move]:
        board = state.board
        moves = list(state.legal_halfmoves())
        def keyf(m):
            if tt_move is not None and m == tt_move:
                return -10_000_000
            if board.is_capture(m):
                return -self._mvv_lva(board, m)
            return 1_000_000
        moves.sort(key=keyf)
        return moves


class RandomEngine:
    name = "random"

    def __init__(self, seed: Optional[int] = None, **_):
        self.rng = random.Random(seed)

    def choose(self, state: GameState) -> chess.Move:
        return self.rng.choice(state.legal_halfmoves())


class GreedyEngine:
    """1-ply material greed; tie-break randomly. Sanity baseline only."""
    name = "greedy"

    def __init__(self, seed: Optional[int] = None, **_):
        self.rng = random.Random(seed)

    def choose(self, state: GameState) -> chess.Move:
        best, best_s = [], None
        sign = 1 if state.mover == WHITE else -1
        for m in state.legal_halfmoves():
            state.push(m)
            out = state.outcome_fast()
            if out is not None and out.winner is not None:
                s = sign * (MATE if out.winner == WHITE else -MATE)
            else:
                s = sign * evaluate(state.board)
            state.pop()
            if best_s is None or s > best_s:
                best, best_s = [m], s
            elif s == best_s:
                best.append(m)
        return self.rng.choice(best)


ENGINES = {"search": SearchEngine, "random": RandomEngine, "greedy": GreedyEngine}

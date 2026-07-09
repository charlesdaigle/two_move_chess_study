"""Rules-kernel tests: every edge case from spec.md, plus playout legality audits."""

import random
import unittest

import chess

from twomove.rules import (ET, IL, KC, WHITE, BLACK, GameState, MATERIAL_SCHEMES,
                           Ruleset)


def state_from_fen(fen, **rs):
    """GameState with an arbitrary board position injected (for edge-case setups)."""
    s = GameState(Ruleset(**rs))
    s.board = chess.Board(fen)
    s.mover = s.board.turn
    s._rep = {}
    s._rep_draw = False
    s._legal_cache = None
    s._bump_repetition(+1)
    return s


class TestSetup(unittest.TestCase):
    def test_start_fens_logical(self):
        for name in MATERIAL_SCHEMES:
            rs = Ruleset(material=name)
            board = chess.Board(rs.start_fen())
            self.assertTrue(board.is_valid(), f"{name}: {rs.start_fen()}")
            # single-mover (black here) always has the full army
            self.assertEqual(len(board.piece_map()),
                             len(MATERIAL_SCHEMES[name]) + 16)

    def test_double_color_black_mirrors(self):
        rs = Ruleset(material="monster4", double_color=BLACK, first_player=BLACK)
        board = chess.Board(rs.start_fen())
        self.assertEqual(board.piece_at(chess.E8), chess.Piece.from_symbol("k"))
        self.assertEqual(board.piece_at(chess.D7), chess.Piece.from_symbol("p"))
        self.assertEqual(board.piece_at(chess.D1), chess.Piece.from_symbol("Q"))

    def test_castling_rights_follow_material(self):
        self.assertIn("KQkq", Ruleset(material="full").start_fen())
        self.assertIn(" kq ", Ruleset(material="monster4").start_fen())


class TestTurnStructure(unittest.TestCase):
    def test_double_mover_moves_twice_then_hands_over(self):
        s = GameState(Ruleset())
        self.assertTrue(s.is_double_turn())
        s.push(chess.Move.from_uci("e2e4"))
        self.assertEqual(s.mover, WHITE)
        self.assertEqual(s.half_index, 1)
        s.push(chess.Move.from_uci("d2d4"))
        self.assertEqual(s.mover, BLACK)
        self.assertEqual(s.half_index, 0)
        self.assertFalse(s.is_double_turn())  # black is the single-mover
        s.push(chess.Move.from_uci("e7e5"))
        self.assertEqual(s.mover, WHITE)

    def test_doubling_period_k2(self):
        s = GameState(Ruleset(k=2))
        self.assertTrue(s.is_double_turn())          # white turn 1: double
        s.push(chess.Move.from_uci("e2e4"))
        s.push(chess.Move.from_uci("d2d4"))
        s.push(chess.Move.from_uci("e7e5"))          # black turn 1
        self.assertFalse(s.is_double_turn())         # white turn 2: single
        s.push(chess.Move.from_uci("g1f3"))
        self.assertEqual(s.mover, BLACK)
        s.push(chess.Move.from_uci("b8c6"))          # black turn 2
        self.assertTrue(s.is_double_turn())          # white turn 3: double again

    def test_pop_roundtrip(self):
        s = GameState(Ruleset(material="no_q", check_regime=ET))
        rng = random.Random(7)
        stack = []
        for _ in range(60):
            if s.outcome() is not None:
                break
            snap = (s.fen(), s.mover, s.half_index, dict(s.turn_no), s.turns_played,
                    s.first_move_to, s.no_progress)
            stack.append(snap)
            s.push(rng.choice(s.legal_halfmoves()))
        while stack:
            s.pop()
            snap = stack.pop()
            self.assertEqual((s.fen(), s.mover, s.half_index, dict(s.turn_no),
                              s.turns_played, s.first_move_to, s.no_progress), snap)


class TestCheckRegimes(unittest.TestCase):
    # White Ra1 + Kg2 vs bare black king a8; white to move on a double turn.
    FEN = "k7/8/8/8/8/8/6K1/R7 w - - 0 1"

    def test_et_first_move_check_ends_turn(self):
        s = state_from_fen(self.FEN, check_regime=ET)
        self.assertIn(chess.Move.from_uci("a1a7"), s.legal_halfmoves())
        s.push(chess.Move.from_uci("a1a7"))  # gives check -> turn ends
        self.assertEqual(s.mover, BLACK)
        self.assertEqual(s.half_index, 0)

    def test_et_non_check_first_move_continues(self):
        s = state_from_fen(self.FEN, check_regime=ET)
        s.push(chess.Move.from_uci("a1b1"))  # quiet -> second half-move
        self.assertEqual(s.mover, WHITE)
        self.assertEqual(s.half_index, 1)

    def test_il_first_move_check_illegal(self):
        s = state_from_fen(self.FEN, check_regime=IL)
        self.assertNotIn(chess.Move.from_uci("a1a7"), s.legal_halfmoves())
        s.push(chess.Move.from_uci("a1b1"))
        # second half-move: checks allowed again
        self.assertIn(chess.Move.from_uci("b1b8"), s.legal_halfmoves())

    def test_kc_king_capture_wins(self):
        s = state_from_fen("k7/8/8/8/8/8/6K1/R7 w - - 0 1", check_regime=KC)
        self.assertIn(chess.Move.from_uci("a1a8"), s.legal_halfmoves())
        s.push(chess.Move.from_uci("a1a8"))
        out = s.outcome()
        self.assertEqual(out.winner, WHITE)
        self.assertEqual(out.reason, "king_capture")
        self.assertEqual(s.legal_halfmoves(), [])

    def test_kc_may_step_into_check(self):
        s = state_from_fen("k7/8/8/8/8/8/r7/1K6 w - - 0 1", check_regime=KC)
        self.assertIn(chess.Move.from_uci("b1a1"),
                      s.legal_halfmoves())  # illegal in orthodox chess

    def test_et_double_mover_must_resolve_check_on_first_half(self):
        # White (double-mover) is in check from the rook on b2; every legal first
        # half-move must resolve the check, exactly as in orthodox chess.
        s = state_from_fen("k7/8/8/8/8/8/1r6/1K5Q w - - 0 1", check_regime=ET)
        moves = s.legal_halfmoves()
        self.assertTrue(moves)
        board = chess.Board(s.fen())
        self.assertTrue(board.is_check())
        for m in moves:
            self.assertTrue(board.is_legal(m))

    def test_checkmate_and_stalemate_detected(self):
        s2 = state_from_fen("k6R/8/1K6/8/8/8/8/8 b - - 0 1", check_regime=ET)
        out = s2.outcome()
        self.assertEqual(out.winner, WHITE)
        self.assertEqual(out.reason, "checkmate")
        s3 = state_from_fen("k7/1R6/1K6/8/8/8/8/8 b - - 0 1", check_regime=ET)
        self.assertEqual(s3.outcome().reason, "stalemate")


class TestSecondMoveRestrictions(unittest.TestCase):
    def test_nc2_blocks_second_half_captures(self):
        s = GameState(Ruleset(nc2=True))
        s.push(chess.Move.from_uci("e2e4"))
        s.push(chess.Move.from_uci("d2d4"))
        s.push(chess.Move.from_uci("d7d5"))
        s.push(chess.Move.from_uci("b1c3"))  # first half: capture exd5 was possible
        moves = s.legal_halfmoves()
        self.assertTrue(all(not chess.Board(s.fen()).is_capture(m) for m in moves))
        self.assertNotIn(chess.Move.from_uci("e4d5"), moves)

    def test_nc2_first_half_captures_allowed(self):
        s = GameState(Ruleset(nc2=True))
        s.push(chess.Move.from_uci("e2e4"))
        s.push(chess.Move.from_uci("g1f3"))
        s.push(chess.Move.from_uci("d7d5"))
        self.assertIn(chess.Move.from_uci("e4d5"), s.legal_halfmoves())

    def test_dp2_same_piece_cannot_move_twice(self):
        s = GameState(Ruleset(dp2=True))
        s.push(chess.Move.from_uci("g1f3"))
        moves = s.legal_halfmoves()
        self.assertTrue(all(m.from_square != chess.F3 for m in moves))

    def test_dp2_promoted_piece_blocked(self):
        # Promotion square must not check the black king (ET would end the turn).
        s = state_from_fen("8/k5P1/8/8/8/8/6K1/8 w - - 0 1", dp2=True)
        s.push(chess.Move.from_uci("g7g8q"))
        self.assertEqual(s.half_index, 1)
        self.assertTrue(all(m.from_square != chess.G8 for m in s.legal_halfmoves()))

    def test_no_second_half_move_passes_turn(self):
        # dp2 with a lone king: no *different* piece exists for the second half-move,
        # so the turn ends after one move (spec edge case: dry second half-move).
        s = state_from_fen("k7/8/8/8/8/8/8/7K w - - 0 1", dp2=True)
        s.push(chess.Move.from_uci("h1g1"))
        self.assertEqual(s.half_index, 0)
        self.assertEqual(s.mover, BLACK)


class TestEnPassant(unittest.TestCase):
    def test_ep_only_against_last_halfmove(self):
        # Black pawn e4; white double turn: 1st half d2d4 (ep e.p. right would arise),
        # 2nd half unrelated -> black must NOT have exd3 e.p.
        s = state_from_fen("k7/8/8/8/4p3/8/3P2K1/8 w - - 0 1", check_regime=ET)
        s.push(chess.Move.from_uci("d2d4"))
        self.assertEqual(s.half_index, 1)
        s.push(chess.Move.from_uci("g2g1"))
        self.assertNotIn(chess.Move.from_uci("e4d3"), s.legal_halfmoves())

    def test_ep_available_when_push_is_last_halfmove(self):
        s = state_from_fen("k7/8/8/8/4p3/8/3P2K1/8 w - - 0 1", check_regime=ET)
        s.push(chess.Move.from_uci("g2g1"))
        s.push(chess.Move.from_uci("d2d4"))  # double push on the SECOND half-move
        self.assertIn(chess.Move.from_uci("e4d3"), s.legal_halfmoves())


class TestDraws(unittest.TestCase):
    def test_threefold_repetition(self):
        # White shuffles the rook out and back within each double turn; black
        # shuffles the king. The start position (white to move) recurs every cycle.
        s = state_from_fen("k7/8/8/8/8/8/8/6RK w - - 0 1", check_regime=ET)
        cycle = ["g1f1", "f1g1", "a8b8", "g1f1", "f1g1", "b8a8"]
        i = 0
        while s.outcome() is None and i < 100:
            s.push(chess.Move.from_uci(cycle[i % len(cycle)]))
            i += 1
        self.assertEqual(s.outcome().reason, "repetition")
        self.assertLessEqual(i, 12)  # two cycles suffice for the threefold

    def test_move_cap(self):
        s = state_from_fen("k7/8/8/8/8/8/8/6RK w - - 0 1", check_regime=ET, cap=3)
        n = 0
        while s.outcome() is None and n < 500:
            s.push(s.legal_halfmoves()[0])
            n += 1
        self.assertIn(s.outcome().reason, ("cap", "no_progress", "repetition"))


class TestPlayoutAudit(unittest.TestCase):
    """Random full games; assert per-half-move legality invariants."""

    def _audit(self, rs, seed):
        import dataclasses
        rs = dataclasses.replace(rs, cap=60)  # ensure termination within the audit
        s = GameState(rs)
        rng = random.Random(seed)
        halfmoves = 0
        while s.outcome() is None and halfmoves < 400:
            moves = s.legal_halfmoves()
            self.assertTrue(moves)
            board = chess.Board(s.fen())
            for m in moves:
                if rs.check_regime == KC:
                    self.assertTrue(board.is_pseudo_legal(m))
                else:
                    self.assertTrue(board.is_legal(m), f"{m} illegal in {s.fen()}")
            if rs.check_regime != KC:
                # both kings always on the board under strict regimes
                self.assertIsNotNone(s.board.king(WHITE))
                self.assertIsNotNone(s.board.king(BLACK))
            s.push(rng.choice(moves))
            halfmoves += 1
        self.assertIsNotNone(s.outcome())

    def test_random_playouts_all_regimes(self):
        for i, (mat, reg) in enumerate([("full", ET), ("no_q_rr", ET), ("monster4", KC),
                                        ("k_pawns6", KC), ("knights_pawns", IL),
                                        ("k_n_pawns", ET)]):
            self._audit(Ruleset(material=mat, check_regime=reg), seed=100 + i)

    def test_random_playouts_with_modifiers(self):
        self._audit(Ruleset(material="no_q_rr", check_regime=ET, nc2=True, dp2=True),
                    seed=42)
        self._audit(Ruleset(material="k_pawns6", check_regime=KC, k=2), seed=43)


if __name__ == "__main__":
    unittest.main()

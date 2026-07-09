"""Engine gate tests (plan.md S0 preconditions, in miniature)."""

import unittest

import chess

from twomove.rules import ET, KC, WHITE, BLACK, GameState, Ruleset
from twomove.engine import GreedyEngine, RandomEngine, SearchEngine, evaluate
from tests.test_rules import state_from_fen


class TestEval(unittest.TestCase):
    def test_startpos_balanced(self):
        self.assertEqual(evaluate(chess.Board()), 0)

    def test_material_sign(self):
        self.assertGreater(evaluate(chess.Board("k7/8/8/8/8/8/8/QK6 w - - 0 1")), 500)
        self.assertLess(evaluate(chess.Board("qk6/8/8/8/8/8/8/K7 w - - 0 1")), -500)


class TestTactics(unittest.TestCase):
    def test_finds_two_halfmove_king_capture_kc(self):
        # White rook a1 can reach the black king in two half-moves: Ra8 is blocked
        # by nothing; make it need two: rook a1 -> a7 -> capture on h7? Simpler:
        # rook must go a1-a6-a8?? Use: rook on b1, king h8: Rb1-b8 is one move (check
        # under ET); under KC white can play Rb8 then Rxh8 next half-move? No: b8-h8
        # same rank -> that IS two half-moves: Rb1-b8, Rb8xh8. Verify engine sees it.
        s = state_from_fen("7k/8/8/8/8/8/6K1/1R6 w - - 0 1", check_regime=KC)
        eng = SearchEngine(nodes=20_000, seed=1, soft_turns=0)
        m1 = eng.choose(s)
        s.push(m1)
        m2 = eng.choose(s)
        s.push(m2)
        out = s.outcome()
        self.assertIsNotNone(out)
        self.assertEqual(out.winner, WHITE)
        self.assertEqual(out.reason, "king_capture")

    def test_single_mover_finds_mate_in_one(self):
        # Black (single-mover) to move: Qb2#, supported by the king on a3.
        s = state_from_fen("8/8/8/8/8/kq6/8/K7 b - - 0 1", check_regime=ET,
                           double_color=WHITE)
        eng = SearchEngine(nodes=20_000, seed=1, soft_turns=0)
        s.push(eng.choose(s))
        out = s.outcome()
        self.assertIsNotNone(out)
        self.assertEqual(out.winner, BLACK)
        self.assertEqual(out.reason, "checkmate")

    def test_avoids_hanging_queen(self):
        # White's queen is attacked by the d5 pawn. After white's FULL double turn
        # (the engine may reorder: king move first, queen move second), black must
        # not have a pawn capture that wins the queen.
        s = state_from_fen("k7/8/8/3p4/4Q3/8/8/K7 w - - 0 1", check_regime=ET)
        eng = SearchEngine(nodes=15_000, seed=1, soft_turns=0)
        s.push(eng.choose(s))
        if s.mover == WHITE:  # second half-move of the turn
            s.push(eng.choose(s))
        board = chess.Board(s.fen())
        for m in board.legal_moves:
            captured = board.piece_type_at(m.to_square)
            self.assertNotEqual(captured, chess.QUEEN,
                                f"queen still hangs to {m.uci()} after {s.fen()}")


class TestGates(unittest.TestCase):
    def _play(self, rs, eng_a, eng_b, max_halfmoves=600):
        """eng_a plays the double side (white here)."""
        s = GameState(rs)
        while s.outcome() is None and len(s._undo) < max_halfmoves:
            eng = eng_a if s.mover == rs.double_color else eng_b
            s.push(eng.choose(s))
        out = s.outcome()
        if out is None or out.winner is None:
            return 0.5
        return 1.0 if out.winner == rs.double_color else 0.0

    def test_search_crushes_random_as_single_mover(self):
        # The hard direction: search plays the SINGLE-mover side with the full army
        # against a random double-mover with a weak army.
        rs = Ruleset(material="k_pawns3", check_regime=ET)
        score = 0.0
        for i in range(4):
            score += self._play(rs, RandomEngine(seed=i),
                                SearchEngine(nodes=1500, seed=i, soft_turns=0))
        self.assertLessEqual(score, 0.5)  # random double-mover scores <= 12.5%/game

    def test_search_beats_greedy_as_double_mover(self):
        rs = Ruleset(material="no_q_rr", check_regime=ET)
        score = 0.0
        for i in range(4):
            score += self._play(rs, SearchEngine(nodes=1500, seed=i, soft_turns=0),
                                GreedyEngine(seed=i))
        self.assertGreaterEqual(score, 3.0)

    def test_push_pop_leaves_state_clean_after_search(self):
        s = GameState(Ruleset(material="no_q", check_regime=ET))
        fen0 = s.fen()
        undo_len = len(s._undo)
        SearchEngine(nodes=4000, seed=3, soft_turns=0).choose(s)
        self.assertEqual(s.fen(), fen0)
        self.assertEqual(len(s._undo), undo_len)
        self.assertEqual(s.half_index, 0)


if __name__ == "__main__":
    unittest.main()

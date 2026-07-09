"""Arena reproducibility and record-shape tests (sharding correctness depends on both)."""

import unittest

from twomove.arena import PointSpec, game_ruleset, play_game
from twomove.rules import BLACK, ET, WHITE, Ruleset


class TestArena(unittest.TestCase):
    def _spec(self, **kw):
        kw.setdefault("games", 4)
        kw.setdefault("nodes", 300)
        return PointSpec(Ruleset(material="k_pawns3", check_regime=ET), **kw)

    def test_games_reproducible(self):
        spec = self._spec()
        a, b = play_game(spec, 1), play_game(spec, 1)
        self.assertEqual(a["moves"], b["moves"])
        self.assertEqual(a["double_score"], b["double_score"])
        self.assertEqual(a["seed"], b["seed"])

    def test_alternate_first_flips_odd_games(self):
        spec = self._spec()
        self.assertEqual(game_ruleset(spec, 0).first_player, WHITE)
        self.assertEqual(game_ruleset(spec, 1).first_player, BLACK)
        self.assertEqual(game_ruleset(spec, 2).first_player, WHITE)

    def test_record_shape(self):
        rec = play_game(self._spec(), 0)
        for key in ("point_id", "ruleset", "game_index", "seed", "double_score",
                    "reason", "n_halfmoves", "n_rounds", "moves"):
            self.assertIn(key, rec)
        self.assertIn(rec["double_score"], (0.0, 0.5, 1.0))


if __name__ == "__main__":
    unittest.main()

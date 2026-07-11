"""Escalation-policy tests for the autonomous campaign queue."""

import json
import os
import tempfile
import unittest

from twomove.queue import (classify, cmd_run, load_queue, main, point_spec,
                           TIERS)


def make_queue(path, campaigns):
    with open(path, "w") as f:
        json.dump({"campaigns": campaigns}, f)


def synth_records(path, spec, scores):
    with open(path, "a") as f:
        for i, s in enumerate(scores):
            f.write(json.dumps({"point_id": spec.point_id, "game_index": i,
                                "double_score": s, "reason": "checkmate",
                                "n_rounds": 20}) + "\n")


def campaign(cid, tier, points, status="active", games=16, nodes=3000):
    return {"id": cid, "tier": tier, "games": games, "nodes": nodes,
            "shard_total": 4, "status": status, "points": points, "verdicts": {}}


class TestClassify(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(classify(0.95, 0.85, 0.99), "decided_double")
        self.assertEqual(classify(0.05, 0.01, 0.15), "decided_single")
        self.assertEqual(classify(0.50, 0.42, 0.58), "certifiable")
        self.assertEqual(classify(0.50, 0.30, 0.70), "ambiguous")
        self.assertEqual(classify(0.43, 0.41, 0.59), "ambiguous")  # off-center


class TestReconcile(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.qfile = os.path.join(self.dir, "campaigns.json")
        self.results = os.path.join(self.dir, "results")
        os.makedirs(self.results)

    def _reconcile(self):
        main(["reconcile", "--file", self.qfile, "--results", self.results])
        return load_queue(self.qfile)

    def test_decided_points_stop_ambiguous_escalate(self):
        pts = [{"material": "k_pawns3", "regime": "ET"},
               {"material": "k_n_pawns", "regime": "ET"}]
        camp = campaign("t0-001", "T0", pts)
        make_queue(self.qfile, [camp])
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pts[0]), [1.0] * 16)          # blowout
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pts[1]), [1.0, 0.0] * 8)      # 50%
        q = self._reconcile()
        done = q["campaigns"][0]
        self.assertEqual(done["status"], "done")
        verdicts = {v["verdict"] for v in done["verdicts"].values()}
        self.assertIn("decided_double", verdicts)
        self.assertIn("ambiguous", verdicts)
        spawned = [c for c in q["campaigns"] if c["id"] != "t0-001"
                   and c.get("note", "").startswith("escalated")]
        self.assertEqual(len(spawned), 1)
        self.assertEqual(spawned[0]["tier"], "T1a")
        self.assertEqual(spawned[0]["games"], TIERS["T1a"][0])
        self.assertEqual([p["material"] for p in spawned[0]["points"]],
                         ["k_n_pawns"])

    def test_incomplete_campaign_untouched_and_promotion(self):
        pts = [{"material": "k_pawns8", "regime": "ET"}]
        camp = campaign("t0-001", "T0", pts)
        nxt = campaign("t2-002", "T2", [{"material": "monster4", "regime": "KC"}],
                       status="pending")
        make_queue(self.qfile, [camp, nxt])
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pts[0]), [1.0] * 7)  # 7 < 16 games
        q = self._reconcile()
        self.assertEqual(q["campaigns"][0]["status"], "active")
        self.assertEqual(q["campaigns"][1]["status"], "pending")

        # finish it -> done, and the pending campaign is promoted
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pts[0]),
                      [1.0] * 16)  # rewrites indices 0..15 (dedup by index)
        q = self._reconcile()
        self.assertEqual(q["campaigns"][0]["status"], "done")
        self.assertEqual(q["campaigns"][1]["status"], "active")

    def test_ladder_bisection_spawns_midpoints(self):
        pts = [{"material": "k_pawns8", "regime": "ET"},
               {"material": "k_pawns6", "regime": "ET"}]
        camp = campaign("t0-001", "T0", pts)
        make_queue(self.qfile, [camp])
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pts[0]), [1.0] * 16)   # double side
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pts[1]), [0.0] * 16)   # single side
        q = self._reconcile()
        bisect = [c for c in q["campaigns"] if c.get("note") == "ladder bisection"]
        self.assertEqual(len(bisect), 1)
        self.assertEqual([p["material"] for p in bisect[0]["points"]],
                         ["k_pawns7"])
        # a second reconcile must not re-spawn the same midpoint
        synth_records(os.path.join(self.results, "b.jsonl"),
                      point_spec(bisect[0], bisect[0]["points"][0]),
                      [0.5] * bisect[0]["games"])
        q = self._reconcile()  # activates bisect campaign
        q = self._reconcile()  # completes it (ambiguous -> escalate)
        again = [c for c in q["campaigns"] if c.get("note") == "ladder bisection"]
        self.assertEqual(len(again), 1)

    def test_t3_certified_goes_to_t4_and_t4_verdicts(self):
        pt = {"material": "k_n_pawns", "regime": "ET"}
        camp = campaign("t3-001", "T3", [pt], games=512)
        make_queue(self.qfile, [camp])
        synth_records(os.path.join(self.results, "a.jsonl"),
                      point_spec(camp, pt), [1.0, 0.0] * 256)  # 0.5, tight CI
        q = self._reconcile()
        gate = [c for c in q["campaigns"] if c["tier"] == "T4"]
        self.assertEqual(len(gate), 1)
        self.assertAlmostEqual(gate[0]["points"][0]["baseline_score"], 0.5)
        self.assertEqual(gate[0]["status"], "active")  # promoted immediately
        # T4 within drift -> balanced
        synth_records(os.path.join(self.results, "b.jsonl"),
                      point_spec(gate[0], gate[0]["points"][0]),
                      [1.0, 0.0] * 64)
        q = self._reconcile()
        v = list(q["campaigns"][1]["verdicts"].values())[0]
        self.assertEqual(v["verdict"], "balanced")


class TestRun(unittest.TestCase):
    def test_unused_slice_exits_clean(self):
        d = tempfile.mkdtemp()
        qfile = os.path.join(d, "campaigns.json")
        make_queue(qfile, [campaign("t0-001", "T0",
                                    [{"material": "k_pawns3", "regime": "ET"}])])
        q = load_queue(qfile)
        q["campaigns"][0]["shard_total"] = 2
        with open(qfile, "w") as f:
            json.dump(q, f)

        class A:
            file, out, workers, slice = qfile, d, 1, 3
        self.assertEqual(cmd_run(A), 0)
        self.assertEqual([f for f in os.listdir(d) if f.endswith(".jsonl")], [])

    def test_seed_queue_is_valid(self):
        q = load_queue("experiments/queue/campaigns.json")
        self.assertTrue(any(c["status"] == "pending" for c in q["campaigns"]))
        for c in q["campaigns"]:
            self.assertIn(c["tier"], TIERS)
            for pt in c["points"]:
                point_spec(c, pt)  # raises on any invalid ruleset field


if __name__ == "__main__":
    unittest.main()

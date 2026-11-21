import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/post-mortem/tools"))
import dropoff  # noqa: E402

XRAY = [[0, 100], [1, 80], [2, 55], [3, 37], [5, 25], [8, 18], [15, 13], [30, 10], [45, 8], [60, 5]]
MID = [[0, 100], [3, 70], [10, 63], [18, 60], [20, 42], [30, 38], [50, 30], [60, 25]]
TWO = [[0, 100], [3, 70], [12, 62], [14, 47], [33, 40], [35, 31], [55, 25], [60, 22]]


def find(points, length=60.0, tooltip=None):
    return dropoff.find_dropoffs(dropoff.load_curve({"points": points}, length), length, tooltip=tooltip)


class TestFindDropoffs(unittest.TestCase):
    def test_hook_drop_like_xray(self):
        r = find(XRAY)
        self.assertTrue(r["main"]["in_hook"])
        self.assertEqual(r["main"]["start"], 0.0)
        self.assertEqual(r["main"]["end"], 3.0)
        self.assertAlmostEqual(r["main"]["lost"], 63.0)
        self.assertIsNone(r["also"])

    def test_mid_cliff_wins(self):
        r = find(MID)
        self.assertFalse(r["main"]["in_hook"])
        self.assertTrue(19 <= r["main"]["at"] <= 20)
        self.assertGreaterEqual(r["main"]["lost"], 8)

    def test_two_drops(self):
        r = find(TWO)
        self.assertTrue(12 <= r["main"]["at"] <= 14)
        self.assertIsNotNone(r["also"])
        self.assertTrue(33 <= r["also"]["at"] <= 35)

    def test_tail_ignored(self):
        r = find([[0, 100], [3, 70], [55, 50], [58, 48], [60, 28]])
        self.assertTrue(r["main"]["in_hook"])

    def test_flat_curve_falls_back_to_hook(self):
        self.assertTrue(find([[0, 100], [3, 60], [30, 45], [60, 30]])["main"]["in_hook"])

    def test_above_100_capped(self):
        curve = dropoff.load_curve({"points": [[0, 112], [3, 70], [30, 50], [60, 30]]}, 60.0)
        self.assertEqual(curve[0], (0.0, 100.0))

    def test_tooltip_sets_the_second(self):
        r = find(MID, tooltip=[19.0, 50])
        self.assertEqual(r["main"]["at"], 19.0)
        r = find(XRAY, tooltip=[3.0, 37])
        self.assertEqual(r["main"]["at"], 3.0)

    def test_too_few_points_errors(self):
        with self.assertRaises(ValueError) as cm:
            dropoff.load_curve({"points": [[0, 100], [3, 50], [60, 5]]}, 60.0)
        self.assertIn("clearer screenshot", str(cm.exception))

    def test_seconds_clamped_to_length(self):
        curve = dropoff.load_curve({"points": [[0, 100], [3, 50], [30, 20], [61, 5]]}, 59.6)
        self.assertEqual(curve[-1][0], 59.6)

    def test_cli_uses_the_reels_length(self):
        run = Path(tempfile.mkdtemp())
        (run / "reel.json").write_text(json.dumps({"status": "ok", "duration": 59.6}), encoding="utf-8")
        (run / "transcript.json").write_text(json.dumps({"words": [], "sentences": []}), encoding="utf-8")
        (run / "curve.json").write_text(json.dumps({"points": MID, "tooltip": None, "end_label": 60}), encoding="utf-8")
        self.assertEqual(dropoff.main([str(run)]), 0)
        out = json.loads((run / "dropoff.json").read_text(encoding="utf-8"))
        self.assertEqual(out["length"], 59.6)
        self.assertFalse(out["main"]["in_hook"])
        self.assertEqual(out["words"]["text"], "")

    def test_cli_unreadable_curve(self):
        run = Path(tempfile.mkdtemp())
        (run / "reel.json").write_text(json.dumps({"status": "ok", "duration": 60}), encoding="utf-8")
        (run / "transcript.json").write_text(json.dumps({"words": [], "sentences": []}), encoding="utf-8")
        (run / "curve.json").write_text(json.dumps({"points": [[0, 100]]}), encoding="utf-8")
        self.assertEqual(dropoff.main([str(run)]), 2)


class TestWordsAt(unittest.TestCase):
    SENT = [{"s": 10.0, "e": 15.5, "text": "A."}, {"s": 15.5, "e": 18.2, "text": "B."},
            {"s": 18.2, "e": 20.5, "text": "C."}, {"s": 20.5, "e": 24.0, "text": "D."},
            {"s": 24.0, "e": 30.0, "text": "E."}]

    def test_words_at_whole_sentences(self):
        r = dropoff.words_at(self.SENT, 19.0, 20.0)
        self.assertEqual(r, {"from": 15.5, "to": 24.0, "text": "B. C. D."})

    def test_words_at_no_speech(self):
        self.assertEqual(dropoff.words_at([], 19.0, 20.0)["text"], "")


if __name__ == "__main__":
    unittest.main()

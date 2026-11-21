import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/post-mortem/tools"))
import transcribe  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


class TestTranscribe(unittest.TestCase):
    def test_parse_whisper_words(self):
        words = transcribe.parse_whisper_json(json.loads((FIX / "whisper_words.json").read_text(encoding="utf-8")))
        self.assertEqual([w["w"] for w in words], ["So", "this", "is", "it.", "Here", "we", "go", "now."])
        self.assertEqual(words[0], {"s": 0.13, "e": 0.17, "w": "So"})
        self.assertEqual(words[-1], {"s": 1.75, "e": 2.0, "w": "now."})

    def test_sentences_split_on_punctuation_and_gaps(self):
        words = [{"s": 0.13, "e": 0.17, "w": "So"}, {"s": 0.17, "e": 0.5, "w": "this"}, {"s": 0.5, "e": 0.68, "w": "is"},
                 {"s": 0.68, "e": 1.17, "w": "it."}, {"s": 1.17, "e": 1.45, "w": "Here"}, {"s": 1.45, "e": 1.59, "w": "we"},
                 {"s": 1.59, "e": 1.75, "w": "go"}]
        out = transcribe.sentences(words)
        self.assertEqual(out, [{"s": 0.13, "e": 1.17, "text": "So this is it."},
                               {"s": 1.17, "e": 1.75, "text": "Here we go"}])
        gap = [{"s": 0.0, "e": 0.4, "w": "first"}, {"s": 0.4, "e": 0.8, "w": "part"},
               {"s": 1.8, "e": 2.2, "w": "second"}, {"s": 2.2, "e": 2.6, "w": "part"}]
        self.assertEqual([x["text"] for x in transcribe.sentences(gap)], ["first part", "second part"])

    def test_empty_words(self):
        self.assertEqual(transcribe.sentences([]), [])
        self.assertEqual(transcribe.parse_whisper_json({"transcription": []}), [])


if __name__ == "__main__":
    unittest.main()


class TestNoFakeWords(unittest.TestCase):
    def test_music_tokens_dropped(self):
        data = {"transcription": [{"offsets": {"from": 0, "to": 500}, "text": " ♪"},
                                  {"offsets": {"from": 500, "to": 900}, "text": " *music*"},
                                  {"offsets": {"from": 900, "to": 1200}, "text": " [Music]"},
                                  {"offsets": {"from": 1200, "to": 1500}, "text": " Hi."}]}
        self.assertEqual([w["w"] for w in transcribe.parse_whisper_json(data)], ["Hi."])

    def test_whisper_cli_suppresses_non_speech(self):
        calls = []

        def run(cmd, **kw):
            calls.append(cmd)
            Path(cmd[cmd.index("-of") + 1] + ".json").write_text('{"transcription": []}', encoding="utf-8")
            from types import SimpleNamespace
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        transcribe._whisper_cli("a.wav", run=run)
        self.assertIn("-sns", calls[0])

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/post-mortem/tools"))
import report  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "run"


def copy_run():
    d = Path(tempfile.mkdtemp()) / "run"
    shutil.copytree(FIX, d)
    return d


def edit(run, name, fn):
    p = run / name
    data = json.loads(p.read_text(encoding="utf-8"))
    fn(data)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestReport(unittest.TestCase):
    def test_graph_marks_the_drop(self):
        h = report.render_html(FIX)
        self.assertIn("<svg", h)
        self.assertIn('class="drop"', h)
        self.assertIn("0:19", h)

    def test_transcript_highlights_drop_lines(self):
        h = report.render_html(FIX)
        self.assertIn('<p class="line hit"><span class="t">0:18</span>Now let me explain the setup again.</p>', h)
        self.assertIn('<p class="line"><span class="t">0:04</span>First I open the project.</p>', h)

    def test_both_rewrites_and_why(self):
        h = report.render_html(FIX)
        for s in ("Close", "Bolder", "You went back to explaining the setup", "Starts lines with So and Now",
                  "this is the part that saves the time", 'class="original"'):
            self.assertIn(s, h)

    def test_also_drop_optional(self):
        h = report.render_html(FIX)
        self.assertNotIn("Also worth a look", h)
        self.assertNotIn('class="stats"', h)
        run = copy_run()
        edit(run, "dropoff.json", lambda d: d.update(
            also={"start": 40.0, "end": 42.0, "at": 41.0, "lost": 5.0, "in_hook": False},
            also_words={"from": 38.0, "to": 43.0, "text": "A later line."}))
        edit(run, "rewrite.json", lambda d: d.update(stats={"Views": "312", "Average watch time": "0:06"}))
        h = report.render_html(run)
        self.assertIn("Also worth a look", h)
        self.assertIn("A later line.", h)
        self.assertIn('class="stats"', h)
        self.assertIn("0:06", h)

    def test_hook_drop_wording(self):
        run = copy_run()
        edit(run, "dropoff.json", lambda d: d.update(main={"start": 0.0, "end": 3.0, "at": 2.0, "lost": 62.0, "in_hook": True}))
        self.assertIn("in the hook", report.render_html(run))

    def test_no_speech_message(self):
        run = copy_run()
        edit(run, "dropoff.json", lambda d: d["words"].update(text=""))
        self.assertIn("No words were spoken at this point", report.render_html(run))

    def test_escaping(self):
        h = report.render_html(FIX)
        self.assertNotIn("<b>&", h)
        self.assertIn("&lt;b&gt;&amp;&quot;🔥", h)
        self.assertIn("&lt;now&gt;", h)
        md = report.render_md(FIX)
        self.assertIn('<b>&"🔥', md)
        self.assertIn("Skip the setup <now>.", md)


if __name__ == "__main__":
    unittest.main()

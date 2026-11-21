import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude/skills/post-mortem/SKILL.md"


class TestSkillDoc(unittest.TestCase):
    def test_skill_doc_names_every_step(self):
        text = SKILL.read_text(encoding="utf-8")
        front = re.match(r"---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(front)
        self.assertIn("name: post-mortem", front.group(1))
        for trigger in ("/post-mortem", "why did my reel flop", "where did people drop off", "rewrite my hook"):
            self.assertIn(trigger, front.group(1))
        for must in ("doctor.py", "pull.py", "transcribe.py", "dropoff.py", "report.py", "curve.json", "rewrite.json",
                     "first 3 seconds", "last 3 seconds", "press on the steepest part", "video file"):
            self.assertIn(must, text)

    def test_readme_has_install_and_screenshot(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("github.com/corbinsylk/post-mortem", readme)
        self.assertIn("How long people watched your reel", readme)


if __name__ == "__main__":
    unittest.main()


class TestMishearing(unittest.TestCase):
    def test_skill_says_fix_mishearings_keep_times(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Fix what the transcriber misheard", text)
        self.assertIn("keeping every time as it is", text)

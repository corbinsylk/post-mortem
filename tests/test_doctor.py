import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/post-mortem/tools"))
import doctor  # noqa: E402


def which_all(name):
    return "/usr/bin/" + name


def no_import(_name):
    return False


class DoctorTest(unittest.TestCase):
    def test_all_present_is_ready(self):
        status = doctor.check(which=which_all, can_import=no_import, model_exists=lambda: True)
        self.assertTrue(all(status.values()), status)

    def test_whisper_cli_counts(self):
        status = doctor.check(which=which_all, can_import=no_import, model_exists=lambda: True)
        self.assertTrue(status["whisper"])

    def test_whisper_cli_without_model_is_missing(self):
        status = doctor.check(which=which_all, can_import=no_import, model_exists=lambda: False)
        self.assertFalse(status["whisper"])

    def test_missing_ffmpeg_gives_one_line(self):
        status = doctor.check(
            which=lambda n: None if n == "ffmpeg" else "/usr/bin/" + n,
            can_import=no_import,
            model_exists=lambda: True,
        )
        lines = doctor.fix_lines(status, platform="darwin")
        self.assertEqual(len(lines), 1)
        self.assertIn("ffmpeg", lines[0])


if __name__ == "__main__":
    unittest.main()

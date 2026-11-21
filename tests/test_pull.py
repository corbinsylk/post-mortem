import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/post-mortem/tools"))
import pull  # noqa: E402


class FakeRun:
    """Stands in for subprocess.run: yt-dlp writes a sound file and its info, ffprobe answers, ffmpeg writes the WAV."""

    def __init__(self, fail_download=False, timeout=False):
        self.calls = []
        self.fail_download = fail_download
        self.timeout = timeout

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        if cmd[0] == "yt-dlp":
            if self.timeout:
                raise subprocess.TimeoutExpired(cmd, 120)
            if self.fail_download:
                return SimpleNamespace(returncode=1, stdout="", stderr="ERROR: login required")
            out = Path(cmd[cmd.index("-o") + 1].replace("%(ext)s", "m4a"))
            out.write_bytes(b"sound")
            out.with_name("audio.info.json").write_text('{"description": "My caption"}', encoding="utf-8")
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if cmd[0] == "ffprobe":
            return SimpleNamespace(returncode=0, stdout="59.6\n", stderr="")
        if cmd[0] == "ffmpeg":
            Path(cmd[-1]).write_bytes(b"wav")
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(cmd)


class TestGetSound(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_link_downloads_sound_only(self):
        run = FakeRun()
        r = pull.get_sound("https://www.instagram.com/reel/DfcW-7CywPT/", self.tmp, run=run)
        ytdlp = next(c for c in run.calls if c[0] == "yt-dlp")
        for flag in ("--ignore-config", "--retries", "-f"):
            self.assertIn(flag, ytdlp)
        self.assertEqual(ytdlp[ytdlp.index("--retries") + 1], "0")
        self.assertEqual(ytdlp[ytdlp.index("-f") + 1], "ba/b")
        self.assertFalse(any("cookies" in a for a in ytdlp))
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["kind"], "link")
        self.assertTrue(r["audio"].endswith(".wav"))
        self.assertEqual(r["duration"], 59.6)
        self.assertEqual(r["caption"], "My caption")

    def test_file_source_extracts_sound(self):
        video = self.tmp / "my reel.mp4"
        video.write_bytes(b"video")
        run = FakeRun()
        r = pull.get_sound(str(video), self.tmp / "run", run=run)
        self.assertFalse(any(c[0] == "yt-dlp" for c in run.calls))
        ff = next(c for c in run.calls if c[0] == "ffmpeg")
        self.assertIn("16000", ff)
        self.assertEqual(r["kind"], "file")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["duration"], 59.6)

    def test_failed_link_says_use_file(self):
        r = pull.get_sound("https://www.instagram.com/reel/x/", self.tmp, run=FakeRun(fail_download=True))
        self.assertEqual(r["status"], "failed")
        self.assertIn("send the video file", r["reason"])
        r = pull.get_sound("https://www.instagram.com/reel/x/", self.tmp, run=FakeRun(timeout=True))
        self.assertEqual(r["status"], "failed")
        self.assertIn("send the video file", r["reason"])

    def test_missing_file(self):
        r = pull.get_sound("/no/such/file.mp4", self.tmp, run=FakeRun())
        self.assertEqual(r["status"], "failed")


if __name__ == "__main__":
    unittest.main()


class TestNoYtDlpProgram(unittest.TestCase):
    def test_missing_program_fails_cleanly(self):
        def run(cmd, **kw):
            raise FileNotFoundError(cmd[0])
        r = pull.get_sound("https://www.instagram.com/reel/x/", tempfile.mkdtemp(), run=run)
        self.assertEqual(r["status"], "failed")

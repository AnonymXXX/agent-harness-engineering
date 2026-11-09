from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_private_markers", ROOT / "scripts" / "check_private_markers.py")
markers = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(markers)


def run(*args: str, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class PrivateMarkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run("git", "init", "-b", "main", cwd=self.repo)
        run("git", "config", "user.name", "Harness Test", cwd=self.repo)
        run("git", "config", "user.email", "harness@example.test", cwd=self.repo)
        self.denylist = self.root / "denylist.txt"
        self.denylist.write_text("# comment\nacme-internal\n10\\.9\\.\n", encoding="utf-8")
        self.commit("README.md", "public text\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def commit(self, name: str, content: str) -> str:
        (self.repo / name).write_text(content, encoding="utf-8")
        run("git", "add", name, cwd=self.repo)
        run("git", "commit", "-m", f"update {name}", cwd=self.repo)
        return run("git", "rev-parse", "HEAD", cwd=self.repo)

    def check(self, *argv: str, stdin: str = "") -> int:
        with mock.patch("sys.stdin", io.StringIO(stdin)), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            return markers.main(["--repo", str(self.repo), "--denylist", str(self.denylist), *argv])

    def test_head_scan_passes_clean_tree_and_blocks_marker(self) -> None:
        self.assertEqual(0, self.check())
        self.commit("notes.md", "deploy to ACME-INTERNAL gateway\n")
        self.assertEqual(1, self.check())

    def test_pre_push_scans_intermediate_commits(self) -> None:
        remote = self.root / "remote.git"
        run("git", "init", "--bare", str(remote), cwd=self.root)
        run("git", "remote", "add", "origin", str(remote), cwd=self.repo)
        run("git", "push", "origin", "main", cwd=self.repo)
        self.commit("hosts.md", "db at 10.9.1.2\n")
        tip = self.commit("hosts.md", "db at <placeholder>\n")

        self.assertEqual(0, self.check(tip))
        push_line = f"refs/heads/main {tip} refs/heads/main {'1' * 40}\n"
        self.assertEqual(1, self.check("--pre-push", stdin=push_line))

    def test_missing_denylist_fails_closed(self) -> None:
        self.denylist.unlink()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
            markers.main(["--repo", str(self.repo), "--denylist", str(self.denylist)])
        self.assertEqual(2, raised.exception.code)

    @unittest.skipUnless(markers.DEFAULT_DENYLIST.is_file(), "private denylist is not available on this machine")
    def test_repository_head_has_no_private_markers(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, markers.main(["--repo", str(ROOT), "--denylist", str(markers.DEFAULT_DENYLIST)]))


if __name__ == "__main__":
    unittest.main()

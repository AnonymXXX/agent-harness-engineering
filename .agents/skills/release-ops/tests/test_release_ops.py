from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "release_ops.py"
SPEC = importlib.util.spec_from_file_location("release_ops", MODULE_PATH)
release_ops = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release_ops
SPEC.loader.exec_module(release_ops)


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class PendingCommitTests(unittest.TestCase):
    def test_patch_equivalent_commit_is_not_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Release Test", cwd=repo)
            run("git", "config", "user.email", "release@example.test", cwd=repo)

            source = repo / "settings.txt"
            source.write_text("disabled\n", encoding="utf-8")
            run("git", "add", "settings.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)

            run("git", "switch", "-c", "target", cwd=repo)
            source.write_text("enabled\n", encoding="utf-8")
            run("git", "commit", "-am", "target wording", cwd=repo)

            run("git", "switch", "-c", "source", "main", cwd=repo)
            source.write_text("enabled\n", encoding="utf-8")
            run("git", "commit", "-am", "source wording", cwd=repo)

            pending = release_ops.plus_commits_from_git_cherry(repo, "target", "source")

            self.assertEqual(set(), pending)

    def test_same_subject_and_changed_lines_at_different_locations_stays_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Release Test", cwd=repo)
            run("git", "config", "user.email", "release@example.test", cwd=repo)

            source = repo / "settings.txt"
            source.write_text(
                "first section\ndisabled\nseparator\nsecond section\ndisabled\n",
                encoding="utf-8",
            )
            run("git", "add", "settings.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)

            run("git", "switch", "-c", "target", cwd=repo)
            source.write_text(
                "first section\nenabled\nseparator\nsecond section\ndisabled\n",
                encoding="utf-8",
            )
            run("git", "commit", "-am", "enable setting", cwd=repo)

            run("git", "switch", "-c", "source", "main", cwd=repo)
            source.write_text(
                "first section\ndisabled\nseparator\nsecond section\nenabled\n",
                encoding="utf-8",
            )
            run("git", "commit", "-am", "enable setting", cwd=repo)
            source_sha = run("git", "rev-parse", "HEAD", cwd=repo)

            pending = release_ops.plus_commits_from_git_cherry(repo, "target", "source")

            self.assertEqual({source_sha}, pending)


class ExplicitCommitBatchTests(unittest.TestCase):
    def test_explicit_commits_are_deduplicated_and_sorted_by_source_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Release Test", cwd=repo)
            run("git", "config", "user.email", "release@example.test", cwd=repo)

            source = repo / "settings.txt"
            source.write_text("base\n", encoding="utf-8")
            run("git", "add", "settings.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)

            source.write_text("base\nfirst\n", encoding="utf-8")
            run("git", "commit", "-am", "first feature", cwd=repo)
            first_sha = run("git", "rev-parse", "HEAD", cwd=repo)

            source.write_text("base\nfirst\nsecond\n", encoding="utf-8")
            run("git", "commit", "-am", "second feature", cwd=repo)
            second_sha = run("git", "rev-parse", "HEAD", cwd=repo)

            commits = release_ops.resolve_explicit_commits(
                repo,
                "main",
                [second_sha[:12], first_sha[:12], second_sha],
            )

            self.assertEqual([first_sha, second_sha], [commit.sha for commit in commits])


    def test_list_commits_follows_branch_order_not_author_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Release Test", cwd=repo)
            run("git", "config", "user.email", "release@example.test", cwd=repo)
            for name, date in (("base", "2026-01-01T00:00:00"), ("parent", "2026-01-03T00:00:00"), ("child", "2026-01-02T00:00:00")):
                (repo / f"{name}.txt").write_text(name, encoding="utf-8")
                run("git", "add", f"{name}.txt", cwd=repo)
                subprocess.run(
                    ["git", "commit", "-m", name, "--date", date],
                    cwd=repo, check=True, capture_output=True,
                )

            commits = release_ops.list_commits(repo, "main", None, None)

            self.assertEqual(["base", "parent", "child"], [commit.subject for commit in commits])


def init_release_repo(root: Path, files: dict[str, str]) -> Path:
    origin = root / "origin.git"
    repo = root / "work"
    run("git", "init", "--bare", "-b", "release", str(origin), cwd=root)
    run("git", "clone", "-q", str(origin), str(repo), cwd=root)
    run("git", "config", "user.name", "Release Test", cwd=repo)
    run("git", "config", "user.email", "release@example.test", cwd=repo)
    for name, content in files.items():
        (repo / name).write_bytes(content.encode("utf-8"))
    run("git", "add", "-A", cwd=repo)
    run("git", "commit", "-m", "base", cwd=repo)
    run("git", "tag", "v3.23.7", cwd=repo)
    run("git", "push", "-q", "origin", "HEAD:release", "v3.23.7", cwd=repo)

    run("git", "switch", "-c", "uat", cwd=repo)
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    run("git", "add", "feature.txt", cwd=repo)
    run("git", "commit", "-m", "fix: 修复合同金额判空", cwd=repo)
    run("git", "push", "-q", "origin", "uat", cwd=repo)
    run("git", "fetch", "-q", "origin", cwd=repo)
    return repo


def release_analysis(repo: Path) -> release_ops.Analysis:
    return release_ops.Analysis(
        mode="execute",
        repo=str(repo),
        source_branch="uat",
        source_ref="origin/uat",
        target_branch="release",
        target_ref="origin/release",
        author="Release Test",
        since=None,
        until=None,
        feature=None,
        commit_selectors=[],
        pending_count=1,
        pending_commits=release_ops.resolve_explicit_commits(repo, "origin/uat", ["uat"]),
        related_other_author_commits=[],
        suggested_bump="patch",
        bump_confidence="high",
        blockers=[],
        warnings=[],
        threshold_exceeded=False,
        needs_confirmation=False,
        latest_reachable_tag="v3.23.7",
        proposed_tag="v3.23.8",
        package_version_change=release_ops.package_version_change(repo, "origin/release", "v3.23.8"),
        matched_count=1,
        selected_cluster_count=0,
    )


class ReleaseCommitTests(unittest.TestCase):
    def test_set_package_version_keeps_formatting_and_dependency_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package.json"
            package.write_bytes(b'{\r\n    "name": "csc",\r\n    "version" : "3.2.8"\r\n}\r\n')
            lock = Path(tmp) / "package-lock.json"
            lock.write_bytes(
                (
                    '{\n  "name": "csc",\n  "version": "3.2.8",\n  "lockfileVersion": 3,\n'
                    '  "packages": {\n    "": {\n      "name": "csc",\n      "version": "3.2.8"\n    },\n'
                    '    "node_modules/dep": {\n      "version": "3.2.8"\n    }\n  }\n}\n'
                ).encode("utf-8")
            )

            self.assertTrue(release_ops.set_package_version(package, "3.23.8"))
            self.assertTrue(release_ops.set_package_version(lock, "3.23.8"))

            self.assertEqual(
                b'{\r\n    "name": "csc",\r\n    "version" : "3.23.8"\r\n}\r\n',
                package.read_bytes(),
            )
            self.assertEqual(
                ["3.23.8", "3.23.8", "3.2.8"],
                [match.group(1) for match in re.finditer(r'"version": "([^"]+)"', lock.read_text())],
            )

    def test_execute_commits_package_version_and_tags_release_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_release_repo(
                Path(tmp),
                {"package.json": '{\n  "name": "csc",\n  "version": "3.2.8"\n}\n'},
            )
            analysis = release_analysis(repo)
            self.assertEqual("package.json 3.2.8 -> 3.23.8", analysis.package_version_change)

            execution = release_ops.execute_plan(repo, analysis)

            run("git", "fetch", "-q", "--tags", "origin", cwd=repo)
            self.assertEqual(
                ["chore: release v3.23.8", "fix: 修复合同金额判空", "base"],
                run("git", "log", "--format=%s", "origin/release", cwd=repo).splitlines(),
            )
            self.assertEqual(execution["releaseCommit"], run("git", "rev-parse", "origin/release", cwd=repo))
            self.assertIn('"version": "3.23.8"', run("git", "show", "origin/release:package.json", cwd=repo))
            self.assertEqual("tag", run("git", "cat-file", "-t", "v3.23.8", cwd=repo))
            self.assertEqual("chore: release v3.23.8", run("git", "tag", "-l", "--format=%(contents:subject)", "v3.23.8", cwd=repo))
            self.assertEqual(execution["releaseCommit"], run("git", "rev-parse", "v3.23.8^{commit}", cwd=repo))
            self.assertEqual("uat", execution["restoredBranch"])

    def test_execute_without_package_version_only_creates_annotated_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_release_repo(Path(tmp), {"build.gradle": "version '1.0-SNAPSHOT'\n"})
            analysis = release_analysis(repo)
            self.assertIsNone(analysis.package_version_change)

            execution = release_ops.execute_plan(repo, analysis)

            run("git", "fetch", "-q", "--tags", "origin", cwd=repo)
            self.assertIsNone(execution["releaseCommit"])
            self.assertEqual(
                "fix: 修复合同金额判空",
                run("git", "log", "-1", "--format=%s", "origin/release", cwd=repo),
            )
            self.assertEqual("tag", run("git", "cat-file", "-t", "v3.23.8", cwd=repo))
            self.assertEqual(
                run("git", "rev-parse", "origin/release", cwd=repo),
                run("git", "rev-parse", "v3.23.8^{commit}", cwd=repo),
            )


    def test_failed_cherry_pick_leaves_target_branch_and_tags_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_release_repo(Path(tmp), {"build.gradle": "version '1.0-SNAPSHOT'\n"})
            (repo / "other.txt").write_text("from uat\n", encoding="utf-8")
            run("git", "add", "other.txt", cwd=repo)
            run("git", "commit", "-m", "fix: 第二个修复", cwd=repo)
            run("git", "push", "-q", "origin", "uat", cwd=repo)
            run("git", "switch", "-q", "-c", "tmp", "origin/release", cwd=repo)
            (repo / "other.txt").write_text("conflicting\n", encoding="utf-8")
            run("git", "add", "other.txt", cwd=repo)
            run("git", "commit", "-m", "hotfix on release", cwd=repo)
            run("git", "push", "-q", "origin", "tmp:release", cwd=repo)
            run("git", "switch", "-q", "uat", cwd=repo)
            run("git", "branch", "-D", "tmp", cwd=repo)
            run("git", "fetch", "-q", "origin", cwd=repo)
            remote_before = run("git", "rev-parse", "origin/release", cwd=repo)

            with self.assertRaises(release_ops.GitCommandError) as raised:
                analysis = release_analysis(repo)
                analysis.pending_commits = release_ops.resolve_explicit_commits(
                    repo, "origin/uat", ["uat~1", "uat"]
                )
                release_ops.execute_plan(repo, analysis, sync_target=True)

            self.assertIn("cherry-pick", str(raised.exception))

            run("git", "fetch", "-q", "--tags", "origin", cwd=repo)
            self.assertEqual(remote_before, run("git", "rev-parse", "origin/release", cwd=repo))
            self.assertEqual(remote_before, run("git", "rev-parse", "release", cwd=repo))
            self.assertEqual("", run("git", "tag", "-l", "v3.23.8", cwd=repo))
            self.assertEqual("uat", run("git", "branch", "--show-current", cwd=repo))
            self.assertEqual("", run("git", "status", "--porcelain", cwd=repo))


if __name__ == "__main__":
    unittest.main()

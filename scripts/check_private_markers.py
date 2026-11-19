#!/usr/bin/env python3
"""Block private markers (company names, internal hosts) from reaching this public repository.

The denylist lives outside this repository so the patterns themselves stay private. Each
non-empty, non-comment line is a case-insensitive extended regular expression.

Usage:
  check_private_markers.py [--repo DIR] [--denylist FILE] [REV ...]
  check_private_markers.py --pre-push        # read `git push` ref lines from stdin

Without REV it scans HEAD. With --pre-push it scans every commit being pushed that no
`origin` branch already contains, so a marker added and later removed is still caught.
Each revision is checked for file contents, file paths, author and committer names and
emails, and the commit message; a pushed annotated tag's message is checked as well.
Exit 0 when clean, 1 on any hit, 2 when the denylist is missing or git fails.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_DENYLIST = Path.home() / ".config/agent-harness/public-denylist.txt"
ZERO_SHA = "0" * 40


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and proc.returncode != 0:
        print(f"ERROR: git {' '.join(args)} failed: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return proc


def load_patterns(path: Path) -> list[str]:
    if not path.is_file():
        print(f"ERROR: private denylist not found: {path} (set HARNESS_PRIVATE_DENYLIST)", file=sys.stderr)
        sys.exit(2)
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    patterns = [line for line in lines if line and not line.startswith("#")]
    if not patterns:
        print(f"ERROR: private denylist is empty: {path}", file=sys.stderr)
        sys.exit(2)
    return patterns


def pushed_objects(repo: Path, stdin_lines: list[str]) -> tuple[list[str], list[str]]:
    """Return (commits, annotated tag objects) that this push would publish."""
    commits: list[str] = []
    tags: list[str] = []
    for line in stdin_lines:
        parts = line.split()
        if len(parts) != 4 or parts[1] == ZERO_SHA:
            continue  # malformed line or a branch deletion
        if git(repo, "cat-file", "-t", parts[1]).stdout.strip() == "tag":
            tags.append(parts[1])
        listing = git(repo, "rev-list", parts[1], "--not", "--remotes=origin")
        commits.extend(listing.stdout.split())
    return list(dict.fromkeys(commits)), list(dict.fromkeys(tags))


def grep_text(text: str, patterns: list[str], label: str) -> list[str]:
    """Match text with the same case-insensitive ERE semantics as `git grep -i -E`."""
    args = ["grep", "-n", "-i", "-E"]
    for pattern in patterns:
        args += ["-e", pattern]
    proc = subprocess.run(args, input=text, capture_output=True, text=True)
    if proc.returncode == 1:
        return []
    if proc.returncode != 0:
        print(f"ERROR: grep failed on {label}: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return [f"{label}:{hit}" for hit in proc.stdout.splitlines()]


def scan(repo: Path, revs: list[str], denylist: Path, tags: list[str] | None = None) -> list[str]:
    patterns = load_patterns(denylist)
    args = ["grep", "-n", "-I", "-i", "-E"]
    for pattern in patterns:
        args += ["-e", pattern]
    hits: list[str] = []
    for rev in revs:
        proc = git(repo, *args, rev, "--", ".", check=False)
        if proc.returncode not in (0, 1):
            print(f"ERROR: git grep failed on {rev}: {proc.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
        hits.extend(proc.stdout.splitlines())
        meta = git(repo, "log", "-1", "--format=%an%n%ae%n%cn%n%ce%n%B", rev).stdout
        hits.extend(grep_text(meta, patterns, f"{rev[:12]} metadata"))
        paths = git(repo, "ls-tree", "-r", "--name-only", rev).stdout
        hits.extend(grep_text(paths, patterns, f"{rev[:12]} path"))
    for tag in tags or []:
        hits.extend(grep_text(git(repo, "cat-file", "-p", tag).stdout, patterns, f"tag {tag[:12]}"))
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("revs", nargs="*")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--denylist",
        type=Path,
        default=Path(os.environ.get("HARNESS_PRIVATE_DENYLIST", DEFAULT_DENYLIST)).expanduser(),
    )
    parser.add_argument("--pre-push", action="store_true", help="Read git pre-push ref lines from stdin")
    args = parser.parse_args(argv)

    repo = Path(git(args.repo, "rev-parse", "--show-toplevel").stdout.strip())
    tags: list[str] = []
    if args.pre_push:
        revs, tags = pushed_objects(repo, sys.stdin.read().splitlines())
    else:
        revs = args.revs or ["HEAD"]
    if not revs and not tags:
        return 0
    hits = scan(repo, revs, args.denylist, tags)
    if hits:
        print("Private markers found; remove them before publishing:", file=sys.stderr)
        for hit in hits[:50]:
            print(f"  {hit[:200]}", file=sys.stderr)
        return 1
    print(f"Private marker check passed ({len(revs)} revision(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

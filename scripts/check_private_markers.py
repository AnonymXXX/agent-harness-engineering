#!/usr/bin/env python3
"""Block private markers (company names, internal hosts) from reaching this public repository.

The denylist lives outside this repository so the patterns themselves stay private. Each
non-empty, non-comment line is a case-insensitive extended regular expression.

Usage:
  check_private_markers.py [--repo DIR] [--denylist FILE] [REV ...]
  check_private_markers.py --pre-push        # read `git push` ref lines from stdin

Without REV it scans HEAD. With --pre-push it scans every commit being pushed that no
`origin` branch already contains, so a marker added and later removed is still caught.
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


def pushed_commits(repo: Path, stdin_lines: list[str]) -> list[str]:
    commits: list[str] = []
    for line in stdin_lines:
        parts = line.split()
        if len(parts) != 4 or parts[1] == ZERO_SHA:
            continue  # malformed line or a branch deletion
        listing = git(repo, "rev-list", parts[1], "--not", "--remotes=origin")
        commits.extend(listing.stdout.split())
    return list(dict.fromkeys(commits))


def scan(repo: Path, revs: list[str], denylist: Path) -> list[str]:
    args = ["grep", "-n", "-I", "-i", "-E"]
    for pattern in load_patterns(denylist):
        args += ["-e", pattern]
    hits: list[str] = []
    for rev in revs:
        proc = git(repo, *args, rev, "--", ".", check=False)
        if proc.returncode == 1:
            continue  # no match
        if proc.returncode != 0:
            print(f"ERROR: git grep failed on {rev}: {proc.stderr.strip()}", file=sys.stderr)
            sys.exit(2)
        hits.extend(proc.stdout.splitlines())
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
    revs = pushed_commits(repo, sys.stdin.read().splitlines()) if args.pre_push else (args.revs or ["HEAD"])
    if not revs:
        return 0
    hits = scan(repo, revs, args.denylist)
    if hits:
        print("Private markers found; remove them before publishing:", file=sys.stderr)
        for hit in hits[:50]:
            print(f"  {hit[:200]}", file=sys.stderr)
        return 1
    print(f"Private marker check passed ({len(revs)} revision(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

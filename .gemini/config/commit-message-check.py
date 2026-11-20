#!/usr/bin/env python3
"""Antigravity PreToolUse hook: run the git-auto-commit message check on `run_command`.

Antigravity sends `{"toolCall": {"name": "run_command", "args": {"CommandLine": ..., "Cwd": ...}}}`
on stdin and expects `{"decision": ...}` on stdout. The shared check script reads the Claude Code
hook shape (`tool_input.command`, `cwd`) and exits 2 with the reason on stderr, so this wrapper
translates both ways. Anything it cannot read is allowed through, like the shared script.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

SCRIPT = os.path.expanduser("~/.agents/skills/git-auto-commit/scripts/check_commit_message.py")


def decide(payload: object) -> dict[str, str]:
    call = payload.get("toolCall") if isinstance(payload, dict) else None
    if not isinstance(call, dict) or call.get("name") != "run_command":
        return {"decision": "allow"}
    args = call.get("args") if isinstance(call.get("args"), dict) else {}
    command = args.get("CommandLine")
    if not isinstance(command, str) or "git" not in command or "commit" not in command:
        return {"decision": "allow"}
    shared = {"tool_name": "Bash", "tool_input": {"command": command}}
    if isinstance(args.get("Cwd"), str):
        shared["cwd"] = args["Cwd"]
    try:
        result = subprocess.run(
            [sys.executable, SCRIPT],
            input=json.dumps(shared),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"decision": "allow"}
    if result.returncode == 2:
        return {"decision": "deny", "reason": result.stderr.strip()}
    return {"decision": "allow"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = None
    print(json.dumps(decide(payload), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

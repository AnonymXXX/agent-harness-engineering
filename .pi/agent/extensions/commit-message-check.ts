/**
 * Commit message check
 *
 * Runs the git-auto-commit hook script before every bash call and blocks `git commit`
 * when the message breaks its rules (subject over 50 characters, several changes in the
 * subject without a body, and so on). The script reads the same JSON as a Claude Code
 * PreToolUse hook and exits 2 with the reason on stderr.
 */

import { spawnSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const SCRIPT = join(homedir(), ".agents/skills/git-auto-commit/scripts/check_commit_message.py");

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		if (event.toolName !== "bash") return undefined;
		const command = event.input.command as string;
		if (!/\bgit\b/.test(command) || !/\bcommit\b/.test(command)) return undefined;

		const result = spawnSync("python3", [SCRIPT], {
			input: JSON.stringify({ tool_name: "Bash", tool_input: { command }, cwd: ctx.cwd }),
			encoding: "utf8",
			timeout: 10_000,
		});
		if (result.status === 2) return { block: true, reason: result.stderr.trim() };
		return undefined;
	});
}

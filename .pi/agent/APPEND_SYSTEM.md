# Harness Engineering Platform Adapter (Pi)

The global `AGENTS.md` (linked to `~/.codex/AGENTS.md`) is the behavioral source of truth. Apply it in Pi with these platform mappings:

- Relative `docs/workflows/...` links in `AGENTS.md` resolve under `~/.codex/`, for example `~/.codex/docs/workflows/git-worktree.md`.
- Pi discovers user-managed skills from `~/.agents/skills` directly. Do not add copies or symlinks under `~/.pi/agent/skills`.
- `request_user_input` / structured choice prompts have no Pi equivalent: ask in chat with short numbered options and wait for the user's reply.
- Pi has no subagents or plan mode. Do the work directly; when a plan is useful, state it briefly in chat.
- Pi does not prompt before tool calls. Before permanent deletion, bulk overwrite, history-discarding Git operations, or any externally visible action, stop and get explicit approval in chat. Prefer `/usr/bin/trash` for local deletion.
- Name task branches `pi/<task-slug>`, never `codex/<task-slug>`; periodic Harness cleanup recognizes the `pi/` prefix.

## Browser

Follow the global Browser And Web Access rule and `~/.codex/docs/workflows/browser.md`. When the `magpie-browser` MCP is connected (configured in `~/.pi/agent/mcp.json`), it is the default browser. Pi has no built-in browser to fall back to: if `magpie-browser` is unavailable, say so and stop that step instead of scripting a browser through AppleScript, shell wrappers, or `ego-browser`. Official docs, APIs, and CLIs remain available through `bash` per the skill/MCP/API → CLI → browser order.

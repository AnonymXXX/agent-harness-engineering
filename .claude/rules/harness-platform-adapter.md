# Harness Engineering Platform Adapter

The shared `~/.claude/CLAUDE.md` links to `~/.codex/AGENTS.md` and remains the behavioral source of truth. Apply it in Claude Code with these platform mappings:

**Language (hard rule):** when the user writes in Chinese, every visible sentence is Chinese, including one-line progress notes between tool calls, background-job narration, and replies after context compaction. Commands, paths, code symbols, and quoted errors stay unchanged.

- Relative `docs/workflows/...` links in `~/.claude/CLAUDE.md` resolve under `~/.codex/`, for example `~/.codex/docs/workflows/git-worktree.md`.
- `request_user_input` maps to `AskUserQuestion`.
- Subagents follow the global Subagent Delegation rule and use the `Agent` tool directly; no Worker protocol, dispatch contract, or delegation quota applies.
- Name task branches `claude/<task-slug>`, never `codex/<task-slug>`; periodic Harness cleanup recognizes the `claude/` prefix. `EnterWorktree` creates `claude/<name>` worktrees under `<repo>/.claude/worktrees/`; use it when the runtime requires isolation (for example a background job), and cleanup handles that location. Otherwise the Git Worktree Workflow's necessity criteria decide. Before calling `EnterWorktree`, run `git rev-parse --show-toplevel`: keep working if the session is already in the intended task worktree, and `cd` into the target repository first if it is outside any Git repository.
- Waiting: run deploys, uploads, builds, SSH sessions, and anything expected to take more than about a minute with `run_in_background`, and wait for a condition with `Monitor`. Never wait with a foreground `sleep` or a `for … seq` polling loop.

## Browser

The global Browser And Web Access and Human Verification rules map to Claude's own browsers in Claude Code. The skill/MCP/API → CLI → browser order still applies.

- Default to the built-in browser pane (`mcp__Claude_Browser__*`).
- Use Claude in Chrome (`mcp__claude-in-chrome__*`) only when the task needs the user's Chrome sign-ins or the user asks for Chrome.
- Login-wall switch: when the built-in pane lands on a login page or needed content/search requires sign-in, switch to Claude in Chrome instead of settling for public content. If Chrome is also signed out, hand off login per the human-verification rule. A site-safety or permission refusal is not a login wall; do not switch browsers to get around it.
- Never compete with the user for control. In Chrome, call `tabs_context_mcp` first, work only in tabs Claude created in its own window/tab group, never focus, reuse, navigate, or close the user's tabs unless asked, and close Claude-created tabs when done unless the user wants them kept. If the user is acting in a page Claude needs, wait for them instead of taking over.
- The global element-first browser rule maps to `find` and `read_page` (`filter: "interactive"`) to locate elements, `computer` clicks by `ref` (not `coordinate`), `form_input` for fields, and `get_page_text` / `find` to read and verify results. If the page's framework ignores a `form_input` value (submit does nothing), click the field by `ref` and use `type` / `key` instead. Use `screenshot` (`scale` ≈ 0.5) or `zoom`, and coordinate clicks, only for genuinely visual content or when no usable `ref` exists. The token-saving rule maps to `browser_batch` for predictable step sequences.
- On CAPTCHA or human verification, stop operating that page, tell the user the page/URL/step, and ask via `AskUserQuestion` with `已验证`, `未处理`, and `取消任务`; resume only after `已验证`.

User-managed Skill sources remain under `~/.agents/skills`. Entries under `~/.claude/skills` are discovery symlinks only.

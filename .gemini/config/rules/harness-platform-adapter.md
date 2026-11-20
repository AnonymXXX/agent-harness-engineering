---
trigger: always_on
description: Harness Engineering platform mappings for Antigravity CLI (agy); applies to every task.
---

# Harness Engineering Platform Adapter (Antigravity CLI)

The global `~/.gemini/AGENTS.md` (linked to `~/.codex/AGENTS.md`) is the behavioral source of truth. Apply it in Antigravity CLI (`agy`) with these platform mappings:

**Language (hard rule):** when the user writes in Chinese, every visible sentence is Chinese, including one-line progress notes between tool calls and replies after context compaction. Commands, paths, code symbols, and quoted errors stay unchanged.

- Relative `docs/workflows/...` links in `AGENTS.md` resolve under `~/.codex/`, for example `~/.codex/docs/workflows/git-worktree.md`.
- User-managed skills stay in `~/.agents/skills`. Antigravity reads global skills from `~/.gemini/config/skills/`; entries there are discovery symlinks only (`../../../.agents/skills/<name>`), never copies. After adding, removing, or renaming a skill, update its link there as well as under `~/.claude/skills`, then run the index commands under Skill Location.
- `request_user_input` maps to `ask_question`. Its answer is the user's own answer and authorizes what it selects; never re-ask an answered question in plain text.
- Subagents follow the global Subagent Delegation rule through `invoke_subagent`; no Worker protocol, dispatch contract, or delegation quota applies.
- Shell commands run through `run_command`. Run deploys, uploads, builds, SSH sessions, and anything expected to take more than about a minute asynchronously (short `WaitMsBeforeAsync`) and follow them with `manage_task`; never wait with a foreground `sleep` or a polling loop. Use `schedule` only for timers or recurring jobs the user asked for.
- Auto-approve modes and `--dangerously-skip-permissions` do not lift the global Destructive Operations rules: before permanent deletion, bulk overwrite, history-discarding Git operations, or any externally visible action that is not already authorized, get explicit approval through `ask_question`. Never use `ask_permission` or permission overrides to get around a denied action.
- Name task branches `agy/<task-slug>`, never `codex/<task-slug>`; periodic Harness cleanup recognizes the `agy/` prefix. When the Git workflow calls for a task worktree, create it with `git worktree add <repo>/.claude/worktrees/<slug> -b agy/<slug>` (the location the global Git ignore and cleanup already cover) and use absolute paths inside it.
- `~/.gemini/config/hooks.json` runs the git-auto-commit message check before every `run_command`. A `deny` from it means the commit message breaks the git-auto-commit rules: load that skill and rewrite the message; do not work around the hook.
- For Facts And Queries, use `search_web` and `read_url_content` (or official CLIs/APIs through `run_command`) before answering.

## Browser

The global Browser And Web Access and Human Verification rules, and `~/.codex/docs/workflows/browser.md`, apply unchanged. The skill/MCP/API → CLI → browser order still applies.

- Default to the `magpie-browser` MCP registered in `~/.gemini/config/mcp_config.json`. Fall back to Antigravity's own browser tools or the Chrome DevTools plugin only when magpie-browser is unavailable or lacks a needed capability, and say why before falling back. Never use `ego-browser`.
- Work only in tabs the agent opened; never take over, navigate, or close the user's tabs.
- On CAPTCHA or human verification, stop operating that page, tell the user the page/URL/step, and ask through `ask_question` with `已验证`, `未处理`, and `取消任务`; resume only after `已验证`.

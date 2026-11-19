# Agent Harness Engineering

[简体中文](README.md) | **English**

A versioned engineering workflow for coding agents (Codex, Claude Code, Pi). It helps the agent choose
an execution approach based on task risk, route work to the appropriate skills, isolate medium- and
high-risk changes when needed, perform proportionate validation, and preserve only project knowledge
that should remain durable.

All three agents share one set of global rules, `.codex/AGENTS.md`; platform differences live in
adapter files.

You do not need to read every rule first. The recommended starting point is to have the agent you
already use read this repository, explain whether it fits your workflow, and then decide whether to
adopt it.

## Recommended: Let Your Agent Read It First

### 1. Understand the repository

Send this to Codex, Claude Code, or Pi:

```text
Read AnonymXXX/agent-harness-engineering and explain what this repository does, which problems it
solves, its core components, who it is for, and its limitations. Cite specific files from the
repository as evidence instead of only repeating the README.
```

If the repository is already open in your agent, replace its name with "the current repository."

### 2. Analyze the benefits and changes for you

Ask the agent to compare the Harness with the configuration and usage context currently available to it:

```text
Read this repository. Within the scope I authorize and that the current environment can access,
inspect my agent configuration (the rule- and skill-related parts of ~/.codex, ~/.claude, and
~/.pi/agent), installed skills, workflows, and recent usage records. Analyze how my daily usage
would change if I adopted this Harness Engineering setup.

Organize the result as "Current state, Changes after adoption, Practical benefits, Costs or risks,
Recommendation." Cite specific repository files as evidence. Clearly state which records you cannot
access, and do not guess.
```

The agent should compare at least these areas:

| Area | Potential change after adoption |
| --- | --- |
| Risk control | Select Fast, Standard, or Heavy Lane checks and use isolated Git worktrees for medium- and high-risk tasks when needed. |
| Skill routing | Choose focused workflows for code design, diagnosis, domain modeling, TDD, and related work. |
| Validation | Run the smallest credible test, lint, build, or Doctor checks for the affected surface. |
| Git and platform operations | Use reusable workflows for commits, GitHub operations, and releases with explicit stop conditions. Task branches stay local; validated work can be pushed straight to non-production branches such as `dev`, `test`, or `uat`, and the agent asks before cleaning up the worktree. |
| Parallel execution | Subagent delegation is paused (2026-08-06); the main agent completes work directly, and the previous Worker protocol remains recoverable from Git history. |
| Knowledge capture | Add only long-lived rules and decisions that pass the Capture Gate, reducing documentation noise. |
| Recovery and upgrades | Keep a single source of truth through versioned configuration and symlinks; the historical one-command installer remains recoverable from Git history. |

These are workflow capabilities, not mechanisms that every task must use. Simple tasks should remain lightweight.

### 3. Ask the agent to adopt it safely

After deciding that it fits, the agent can perform the inspection, linking, and validation:

```text
Help me adopt AnonymXXX/agent-harness-engineering.

First, inspect ~/.codex, ~/.claude, ~/.pi/agent, ~/.agents/skills, the current Git state, and
potential conflicts without making changes. Do not read, copy, or output credentials, sessions,
memory, caches, or other sensitive runtime data.

Before changing anything, list the affected files, backup strategy, dependencies, and risks. Do not
create symlinks or rewrite files until I confirm. After confirmation, create the documented symlinks
only for the agents I actually use, then run the Skill index checks and Harness Doctor. Finally,
summarize the actual changes, validation results, and whether I need to start a new session to load
the rules and skills.
```

The agent can analyze only content you explicitly authorize in the current task and that the local
environment can access. You must supply inaccessible history, remote data, or configuration from
other devices; the agent should not infer conclusions from missing information.

## Skill Set

- Core workflow: `harness-engineering`, plus the four core engineering skills
  `codebase-design`, `diagnosing-bugs`, `domain-modeling`, and `tdd`.
- Frequently used domain skills: `git-auto-commit`, `github-cli-ops`, `release-ops`,
  `frontend-design`, `develop-uniapp-miniapp`, and `wechat-miniprogram-ci-upload`.

## Installation

These steps target macOS. Install Git, `uv`, GitHub CLI, and at least one agent (Codex CLI, Claude
Code, or Pi), then create the symlinks manually. The shared part for every agent:

```bash
gh repo clone AnonymXXX/agent-harness-engineering ~/.local/share/agent-harness-engineering
H=~/.local/share/agent-harness-engineering
mkdir -p ~/.codex ~/.agents/skills ~/.config/git
ln -s $H/.codex/AGENTS.md ~/.codex/AGENTS.md
ln -s $H/.codex/docs ~/.codex/docs
git -C $H config core.hooksPath .githooks
# Task worktrees live in .claude/worktrees/ inside repositories; ignore it globally so git add . never stages one
grep -qxF '.claude/worktrees/' ~/.config/git/ignore 2>/dev/null || echo '.claude/worktrees/' >> ~/.config/git/ignore
for skill in $H/.agents/skills/*; do
  ln -s "$skill" ~/.agents/skills/
done
```

Then add the part for each agent you use:

```bash
# Codex: commit-message check hook (active after you trust it in Codex's /hooks) and the DESIGN.md template
ln -s $H/.codex/hooks.json ~/.codex/hooks.json
ln -s $H/.codex/templates ~/.codex/templates

# Claude Code: global rules, platform adapter, and skill discovery links
mkdir -p ~/.claude/rules ~/.claude/skills
ln -s ~/.codex/AGENTS.md ~/.claude/CLAUDE.md
ln -s $H/.claude/rules/harness-platform-adapter.md ~/.claude/rules/
for skill in $H/.agents/skills/*; do
  ln -s "../../.agents/skills/$(basename "$skill")" ~/.claude/skills/
done

# Pi: global rules, platform adapter, and commit-message check extension (Pi reads skills from ~/.agents/skills directly)
mkdir -p ~/.pi/agent/extensions
ln -s ~/.codex/AGENTS.md ~/.pi/agent/AGENTS.md
ln -s $H/.pi/agent/APPEND_SYSTEM.md ~/.pi/agent/APPEND_SYSTEM.md
ln -s $H/.pi/agent/extensions/commit-message-check.ts ~/.pi/agent/extensions/
```

Finally, run the checks:

```bash
uv run ~/.agents/skills/harness-engineering/scripts/harness_doctor.py index --write
uv run ~/.agents/skills/harness-engineering/scripts/harness_doctor.py index --check
uv run ~/.agents/skills/harness-engineering/scripts/harness_doctor.py doctor
```

If a link target already exists, move it aside with `/usr/bin/trash` before linking. These steps do
not copy or overwrite the machine-specific `~/.codex/config.toml`, `~/.claude/settings.json`,
credentials, sessions, memory, or caches. Afterwards, start a new agent session to load the global
rules and skills.

- Browser work defaults to the `magpie-browser` MCP (install magpie and register it in each agent);
  Codex's Browser/Chrome plugins or Claude's built-in browser and Claude in Chrome are fallbacks only.
- `~/.claude/settings.json` holds machine settings and is not linked; merge the hooks from
  `.claude/settings.hooks.json` into it.
- The image-generation rule's model shim lives in `.local/share/agent-shims/codex-imagegen/` and works with
  the third-party `baoyu-image-gen` skill; link it with
  `mkdir -p ~/.local/share/agent-shims && ln -s $H/.local/share/agent-shims/codex-imagegen ~/.local/share/agent-shims/`.
- `core.hooksPath` enables the pre-push check `scripts/check_private_markers.py`. It scans every
  commit being pushed and rejects the push on any match against the private denylist (default
  `~/.config/agent-harness/public-denylist.txt`, override with `HARNESS_PRIVATE_DENYLIST`), and also
  when that denylist is missing.

Historical releases provide the one-command installer `scripts/harness_setup.py` and `profiles.json`.
To automate installation, restore those two files from Git history and follow the README of that era.

## Rule Provenance

Adapted from the [official GPT-6 Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices), verified 2026-09-09.
Its eleven examples map to this Harness as follows; these are task-dependent defaults, not eleven
mandatory steps:

| Official examples | Harness application |
| --- | --- |
| 1–3: initiative and follow-through | Global intent rule: act within scope, persist, and prepare authorized work before asking |
| 4–5: skill instruction conflicts | Global hierarchy and exact-source explanation when a skill changes the outcome |
| 6–8: writing style | Global outcome-first prose, reader-appropriate detail, and direct language |
| 9–10: delegation and agent messages | Existing runtime-compatible, bounded delegation; human-readable messages |
| 11: testing and verification | Checks proportional to regression risk; no repetitive testing without new evidence |

## Layout

- `.codex/`: global rules shared by all three agents, Harness workflow documents, the `DESIGN.md` template, and the Codex hook configuration.
- `.claude/`: the Claude Code platform adapter and hook fragment.
- `.pi/`: the Pi platform adapter and commit-message check extension.
- `.local/share/agent-shims/`: the image-generation model shim.
- `scripts/`, `.githooks/`: the public repository's pre-push private-marker check.
- `.agents/skills/`: the Harness skill family and its executable checks.

The repository mirrors paths relative to the user's home directory. Runtime state, sessions,
memories, credentials, caches, and unrelated skills are intentionally excluded.

## Licensing

Except for the third-party components identified in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), this repository is licensed under the
[Apache License 2.0](LICENSE). First-party authorship and scope are recorded in
[ORIGINAL_WORKS.md](ORIGINAL_WORKS.md). Third-party license terms continue to apply independently
to their identified paths and local derivatives.

## Support

If this project improves your agent workflow, you can support its ongoing maintenance on
[Afdian](https://afdian.com/a/codexharness). Sponsorship is optional and does not change the
repository's open-source availability or include paid technical support.

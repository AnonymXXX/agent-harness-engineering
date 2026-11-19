# Agent Harness Engineering

**简体中文** | [English](README.en.md)

一套给编程 Agent（Codex、Claude Code、Pi）用的可版本化工程工作流：让 Agent 按任务风险选择执行方式，
调用合适的 Skill，必要时隔离中高风险修改，完成相称的验证，并只沉淀真正需要长期保留的项目知识。

三个 Agent 共用同一份全局规则 `.codex/AGENTS.md`，各平台的差异写在适配文件里。

你不需要先读完所有规则。推荐直接让你常用的 Agent 阅读本仓库，由它解释是否适合你的使用方式，
再决定是否接入。

## 推荐：先让 Agent 读一遍

### 1. 了解这个仓库

在 Codex、Claude Code 或 Pi 中发送：

```text
请阅读 AnonymXXX/agent-harness-engineering，告诉我这个仓库是干什么的、解决了什么问题、
包含哪些核心组件、适合哪些用户，以及它的限制。请引用仓库中的具体文件作为依据，
不要只复述 README。
```

如果已经在 Agent 中打开了本仓库，可以把仓库名替换为“当前仓库”。

### 2. 分析接入后的收益和改变

让 Agent 结合你当前可访问的配置和使用情况进行个性化比较：

```text
请阅读这个仓库，并在我授权且当前环境可访问的范围内，检查我的 Agent 配置（~/.codex、
~/.claude、~/.pi/agent 中与规则和 Skill 相关的部分）、已安装 Skills、工作流和近期使用记录。
分析如果接入这套 Harness Engineering，我的日常使用会发生什么变化。

请按“当前状态、接入后变化、实际收益、成本或风险、是否建议接入”输出，并引用仓库中的
具体文件作为依据。无法访问的记录请明确说明，不要猜测。
```

Agent 应重点比较以下方面：

| 方面 | 接入后可能发生的变化 |
| --- | --- |
| 风险控制 | 按 Fast、Standard、Heavy Lane 选择检查强度，中高风险任务在必要时使用独立 Git worktree。 |
| Skill 路由 | 根据代码设计、故障诊断、领域建模、TDD 等任务自动选择专业工作流。 |
| 验证 | 根据修改范围运行最小但可信的测试、lint、构建或 Doctor 检查。 |
| Git 与平台操作 | 提交、GitHub 操作和发布走可复用流程并保留明确的停止条件；任务分支只留本地，验证通过后可直接推到 `dev`、`test`、`uat` 等非生产分支，清理 worktree 前先问你。 |
| 并行执行 | 子代理派发当前暂停（2026-08-06），主 Agent 直接完成工作；原 Worker 协议可从 Git 历史恢复。 |
| 知识沉淀 | 只有满足 Capture Gate 的长期规则和决策才进入项目文档，减少文档噪声。 |
| 恢复与升级 | 通过版本化配置和符号链接保持单一事实源；历史一键安装器可从 Git 历史找回。 |

这些是工作流提供的能力，不代表每个任务都会使用全部机制。简单任务仍应保持轻量。

### 3. 让 Agent 安全接入

确认适合后，可以让 Agent 完成检查、链接和验证：

```text
请帮我接入 AnonymXXX/agent-harness-engineering。

先只读检查 ~/.codex、~/.claude、~/.pi/agent、~/.agents/skills、当前 Git 状态和可能冲突。
不要读取、复制或输出凭据、sessions、memory、cache 或其他敏感运行时数据。

修改前列出会影响的文件、备份策略、依赖和风险。在我确认前不要创建符号链接或改写文件。
确认后按 README 的安装说明创建符号链接，只链接我实际在用的 Agent，随后运行 Skill index
检查和 Harness Doctor。最后总结实际变更、验证结果，以及是否需要新开会话来加载规则和 Skills。
```

Agent 只能分析当前任务中你明确授权且本机可访问的内容。它无法访问的历史记录、远程数据或
其他设备配置，必须由你补充；不要根据不完整信息推断结论。

## 技能组成

- 核心工作流：`harness-engineering`，以及 `codebase-design`、`diagnosing-bugs`、
  `domain-modeling`、`tdd` 四个核心工程 Skill。
- 常用领域 Skill：`git-auto-commit`、`github-cli-ops`、`release-ops`、
  `frontend-design`、`develop-uniapp-miniapp`、`wechat-miniprogram-ci-upload`。

## 安装

以下步骤以 macOS 为准。先安装 Git、`uv`、GitHub CLI，以及至少一个 Agent（Codex CLI、Claude Code
或 Pi），然后手动创建符号链接。所有 Agent 共用的部分：

```bash
gh repo clone AnonymXXX/agent-harness-engineering ~/.local/share/agent-harness-engineering
H=~/.local/share/agent-harness-engineering
mkdir -p ~/.codex ~/.agents/skills ~/.config/git
ln -s $H/.codex/AGENTS.md ~/.codex/AGENTS.md
ln -s $H/.codex/docs ~/.codex/docs
git -C $H config core.hooksPath .githooks
# 任务 worktree 放在仓库内的 .claude/worktrees/，全局忽略，避免 git add . 把它当嵌套仓库提交
grep -qxF '.claude/worktrees/' ~/.config/git/ignore 2>/dev/null || echo '.claude/worktrees/' >> ~/.config/git/ignore
for skill in $H/.agents/skills/*; do
  ln -s "$skill" ~/.agents/skills/
done
```

再按你用的 Agent 补上对应部分：

```bash
# Codex：提交信息检查 hook（在 Codex 的 /hooks 中信任后生效）
ln -s $H/.codex/hooks.json ~/.codex/hooks.json

# Claude Code：全局规则、平台适配规则和 Skill 发现链接
mkdir -p ~/.claude/rules ~/.claude/skills
ln -s ~/.codex/AGENTS.md ~/.claude/CLAUDE.md
ln -s $H/.claude/rules/harness-platform-adapter.md ~/.claude/rules/
for skill in $H/.agents/skills/*; do
  ln -s "../../.agents/skills/$(basename "$skill")" ~/.claude/skills/
done

# Pi：全局规则（Pi 直接从 ~/.agents/skills 读取 Skill，不需要另建链接）
mkdir -p ~/.pi/agent
ln -s ~/.codex/AGENTS.md ~/.pi/agent/AGENTS.md
```

最后检查：

```bash
uv run ~/.agents/skills/harness-engineering/scripts/harness_doctor.py index --write
uv run ~/.agents/skills/harness-engineering/scripts/harness_doctor.py index --check
uv run ~/.agents/skills/harness-engineering/scripts/harness_doctor.py doctor
```

链接目标已存在时先用 `/usr/bin/trash` 移走备份再链接。这些步骤不会复制或覆盖机器相关的
`~/.codex/config.toml`、`~/.claude/settings.json`、凭据、sessions、memory 或 cache。
完成后新开一个 Agent 会话，以加载全局规则和 Skills。

- 浏览器默认使用 `magpie-browser` MCP（需安装 magpie 并在各 Agent 中注册），不可用时才回退到
  Codex 的 Browser/Chrome 插件或 Claude 的内置浏览器与 Claude in Chrome。
- `~/.claude/settings.json` 含本机设置，不做链接；把 `.claude/settings.hooks.json` 中的 hook 合并进去即可。
- Pi 的平台适配说明和提交信息检查扩展暂未收录在本仓库，需要时可参照
  `.claude/rules/harness-platform-adapter.md` 自行编写。
- `core.hooksPath` 启用推送前检查 `scripts/check_private_markers.py`：它扫描每个待推送提交，
  命中私有黑名单（默认 `~/.config/agent-harness/public-denylist.txt`，可用 `HARNESS_PRIVATE_DENYLIST`
  指定）即拒绝推送；黑名单缺失时同样拒绝。

历史版本提供一键安装器 `scripts/harness_setup.py` 与 `profiles.json`；如需自动化安装，可从
Git 历史恢复这两个文件后按当时的 README 使用。

## 规则依据

规则改编自 [OpenAI 官方 GPT-6 Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)（核实于 2026-09-09）。
其 11 个示例与 Harness 的对应关系如下，均为按任务取用的默认做法，而非 11 个必经步骤：

| 官方示例 | Harness 落点 |
| --- | --- |
| 1–3：主动性与持续推进 | 全局意图规则：在范围内行动、持续推进，提问前先准备好已授权的结果 |
| 4–5：Skill 指令冲突 | 全局优先级规则；Skill 改变结果时引用确切来源说明 |
| 6–8：写作风格 | 全局的结果先行、按读者调整详略、直接表达 |
| 9–10：委派与 Agent 消息 | 运行时兼容的有界委派；消息对人可读 |
| 11：测试与验证 | 按回归风险选择检查；没有新证据不重复测试 |

## 目录结构

- `.codex/`：三个 Agent 共用的全局规则、Harness 工作流文档与 Codex hook 配置。
- `.claude/`：Claude Code 平台适配规则与 hook 片段。
- `scripts/`、`.githooks/`：公开仓库的推送前私有信息检查。
- `.agents/skills/`：Harness Skill 系列及其可执行检查。

本仓库按照相对于用户主目录的路径镜像文件。运行时状态、会话、记忆、凭据、缓存和无关 Skill
均被有意排除。

## 许可证

除 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 中标明的第三方组件外，本仓库采用
[Apache License 2.0](LICENSE) 许可。第一方作品的作者身份与适用范围记录在
[ORIGINAL_WORKS.md](ORIGINAL_WORKS.md) 中。第三方组件及其本地衍生内容继续独立遵循各自的许可条款。

## 赞助

如果本项目改善了你的 Agent 工作流，可以通过
[爱发电](https://afdian.com/a/codexharness)支持项目的持续维护。赞助完全自愿，不会改变仓库的
开源可用性，也不包含付费技术支持。

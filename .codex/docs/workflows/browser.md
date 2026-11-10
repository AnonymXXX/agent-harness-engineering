# Browser Workflow

The global [Browser And Web Access](../../AGENTS.md#browser-and-web-access) rule owns when a browser may be used and the hard boundaries. This document owns platform choice and page operation. Read it before starting browser work.

## 执行路径

先发现当前可用的专用 MCP/API；本机 CLI 缺失不代表远端 MCP 不可用。官方文档 MCP、API schema 和 CLI help 能覆盖的查询无需启动浏览器。回退到浏览器前说明具体缺失能力或连接故障。

## 平台选择

需要浏览器的联网调研、网页读取、登录态操作和本地页面验证，默认使用 `magpie-browser` MCP（Claude 中工具名为 `mcp__magpie-browser__browser`，Codex 中为 MCP 服务器 `magpie-browser`），不使用平台内置浏览器（Codex Browser 插件/应用内浏览器、Claude 内置浏览器面板 `mcp__Claude_Browser__*`）。它在用户自己的浏览器里打开独立标签页，天然带登录态。

- `magpie-browser` 未连接、报错或缺少任务所需能力时，才回退到平台自带浏览器：Codex 用 Browser 插件，Chrome 登录态需求用 Chrome 插件；Claude Code 按 `~/.claude/rules/harness-platform-adapter.md` 使用内置浏览器面板和 Claude in Chrome。回退前说明具体原因。
- 用户点名其他浏览器或工具时，按用户指定。
- 登录墙（跳转登录页、内容或搜索要求登录）：先用 `browsers` / `use_browser` 确认 magpie 连接的是带登录态的浏览器；仍未登录时按 Human Verification 交给用户登录，不降级为只查公开内容。站点安全策略拦截不属于登录墙，不得换浏览器绕过。
- 操作映射：`snapshot`（`interactive: true`）定位元素，`click` / `type` / `select` 按 `ref` 操作，`text` 读取并核对结果；`screenshot` 仅用于视觉内容。

所选浏览器不可用或缺少任务所需能力时，按对应插件的故障排查流程处理；仍无法覆盖时明确报告限制并停止对应步骤。

## 页面操作

浏览器工作默认在后台进行，只在 Agent 自己新建的标签页、窗口或标签组中操作；除非用户明确指定，不聚焦、接管、导航或关闭用户原有标签页；用户正在操作 Agent 需要的页面时等待用户，不强行接管。任务完成后关闭 Agent 创建的页面，仅在用户要求保留、页面本身是交付物或需要用户继续操作时保留。

元素优先：定位、读取、点击和填写都先用元素查找、可访问性树或页面文本，按元素引用点击、用表单工具填写，并用页面文本或元素查找核对结果；不以截图识图加坐标点击作为常规操作方式。仅在布局、图片、二维码等视觉内容必要，或元素工具无法定位、操作时才截图或按坐标操作，截图优先缩小比例或局部放大。

节省 token：可预判的连续步骤（导航、点击、等待、读取核对）合并为一次批量调用；已知深链直接打开，不逐级点菜单；只加载与当前请求范围相关的 Skill。

## JumpServer Web 终端

执行命令前按全局 Destructive Operations 规则核对资产所属环境。在 JumpServer Web 终端中执行命令时，使用页面底部 `Batch commands` 的命令输入框与 `Send` 按钮；不向 xterm Canvas 的隐藏 textarea 注入文本。命令执行后通过终端视口截图核对输出。

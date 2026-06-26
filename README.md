# 麦麦用 Claude Code CLI 做任务

通过 QQ 命令在 MaiBot（麦麦）所在服务器上运行 [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/overview)，把进度、最终结果和产物文件回传到 QQ。

## 功能

- 支持 `/claude <任务描述>` 触发 Claude Code CLI 本地任务
- 实时转发 NDJSON 流式进度到 QQ
- 任务完成后自动扫描并上传产物（docx/pdf/xlsx/ppt/zip 等）
- 支持 NapCat 文件直传和 SnowLuma OneBot file 段
- 支持 `/claude --dm` 私聊进度推送
- 支持 session 续聊（`/claude session` / `/claude continue`）
- 支持 `/claude mcp` 列出 MCP 服务器
- 支持 `/claude config` 查看配置
- 回复 QQ 文件消息作为输入材料
- 定时清理过期任务记录和输入文件

## 前提条件

1. **MaiBot**（麦麦）已部署运行，版本 1.0.0+
2. **Claude Code CLI** 已安装并认证
   - 安装：`npm install -g @anthropic-ai/claude-code`
   - 认证：`claude auth login`（推荐）或设置 `ANTHROPIC_API_KEY` 环境变量
3. QQ 适配器：NapCat 或 SnowLuma（用于文件上传，可选）

## 安装

```bash
# 1. 进入 MaiBot 插件目录
cd MaiBot/plugins

# 2. 克隆插件
git clone https://github.com/QR-0W/maibot-claude-code-plugin.git qr0w.remote-claude-code-agent

# 3. 重启 MaiBot
```

## 配置

编辑 `plugins/qr0w.remote-claude-code-agent/config.toml`：

### 最小配置（开箱即用）

如果 Claude Code CLI 已安装到 PATH 且认证完成，默认配置即可使用：

```toml
[plugin]
enabled = true

[local_claude]
claude_binary = "claude"

[permission]
allow_all_users = true  # 测试时允许所有用户触发
```

### 完整配置参考

```toml
[local_claude]
# Claude Code CLI 可执行文件路径
claude_binary = "claude"

# 任务根目录（相对路径按插件目录解析）
work_root = "data/tasks"

# 模型（留空使用 Claude Code 默认）
# alias: sonnet, opus, haiku, fable
# full-id: claude-sonnet-4-6, claude-opus-4-8
model = ""

# 最大 agentic turns（0 = 不限制）
max_turns = 20

# 详细输出（用于提取进度）
verbose = true

# 额外 CLI 参数（不要传 --dangerously-skip-permissions 等插件管理的 flag）
extra_args = []

# 传递给子进程的环境变量（如 ANTHROPIC_API_KEY）
pass_env_vars = []

# 进程超时（秒）
process_timeout_seconds = 3600.0
```

## 使用

### 基本用法

```
# 创建一次性任务
/claude 用 Python 写一个 Flask API 统计服务器

# 带私聊进度
/claude --dm 生成一份项目周报

# 创建可续聊 session
/claude session my-project 开发用户认证模块

# 继续上次 session
/claude continue 添加密码重置功能
```

### 子命令

| 命令 | 说明 |
|------|------|
| `/claude status <task_id>` | 查看任务状态 |
| `/claude cancel <task_id>` | 取消任务 |
| `/claude recover <task_id>` | 恢复/重传结果 |
| `/claude list` | 列出我的任务 |
| `/claude clean` | 清理过期记录（管理员） |
| `/claude mcp` | 列出 MCP 服务器 |
| `/claude config` | 查看当前配置 |
| `/claude help` | 查看帮助 |

### Session 管理

| 命令 | 说明 |
|------|------|
| `/claude session <名称> <任务>` | 创建命名 session |
| `/claude continue <任务>` | 继续最近 session |
| `/claude resume <名称>` | 恢复指定 session |
| `/claude list sessions` | 列出所有 session |

### 文件输入

回复 QQ 文件消息后发送 `/claude <任务>`，文件会自动导入到 workspace/input/ 目录。

## 适配器配置

### NapCat（推荐）

在 `config.toml` 中启用 NapCat：

```toml
[napcat]
enabled = true
upload_file = true
```

NapCat 支持 `upload_group_file` / `upload_private_file` API，可直传产物到 QQ。

### SnowLuma

在 `config.toml` 中启用 SnowLuma：

```toml
[snowluma]
enabled = true
send_artifacts_as_file_segments = true
```

## 权限控制

```toml
[permission]
# 是否允许所有用户触发
allow_all_users = false

# 名单模式：whitelist / blacklist
user_list_mode = "whitelist"

# 用户名单（qq:ID）
trigger_users = ["qq:123456789"]

# 管理员（可使用高危配置）
admin_users = ["qq:123456789"]
```

## 目录结构

```
qr0w.remote-claude-code-agent/
├── _manifest.json              # 插件元数据
├── config.toml                 # 运行时配置
├── plugin.py                   # 主实现
├── README.md                   # 本文件
├── .gitignore
└── data/
    └── tasks/
        └── <task_id>/
            ├── prompt.md       # 任务 prompt
            ├── stdout.jsonl    # Claude Code NDJSON 输出
            ├── stderr.log      # stderr 日志
            └── workspace/      # Claude Code 工作目录
                ├── input/      # QQ 文件输入材料
                └── artifacts/  # 生成的产物
```

## 与 Codex 插件的区别

| 特性 | Codex 版本 | Claude Code 版本 |
|------|-----------|-----------------|
| 命令前缀 | `/codex` | `/claude` |
| CLI 输出 | JSONL | stream-json NDJSON |
| 权限控制 | `-a never -s workspace-write` | `--dangerously-skip-permissions` |
| 进度提取 | `item.completed` 事件 | `assistant` / `stream_event` 事件 |
| Skills | 支持 | 不支持（Claude Code 无此功能） |
| Session | Codex thread_id | Claude Code `--session-id` |
| 用户配置 | `~/.codex/config.toml`（TOML） | `~/.claude/settings.json`（JSON） |

## 常见问题

**Q: "找不到 Claude Code CLI 可执行文件"**
A: 确认 `claude` 在 PATH 中，或在 `local_claude.claude_binary` 填写绝对路径。

**Q: 任务运行后没有收到回复**
A: 检查 Claude Code 是否已完成认证（`claude auth status`），确认 `ANTHROPIC_API_KEY` 或 OAuth token 有效。

**Q: 进度消息不更新**
A: 确认 `local_claude.verbose = true`，这会让 Claude Code 输出详细事件流。

**Q: 如何限制花费？**
A: 在 `local_claude.extra_args` 中添加 `"--max-budget-usd", "5.00"`。

## 许可

MIT License

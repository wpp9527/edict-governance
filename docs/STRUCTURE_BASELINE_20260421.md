# 2026-04-21 结构基线与“双太子”修复

## 问题
运行态出现两个“太子”：
- `main`
- `taizi`

二者在生成后的 `agent_config.json` 中都被映射为 `label=太子`，导致控制台/统计层出现重复。

## 根因
1. `openclaw.json` 的 `agents.list` 同时包含 `main` 与 `taizi`
2. `scripts/sync_agent_config.py` 将 `main` 也映射为“太子”
3. 运行环境里 `OPENCLAW_HOME=/opt/fnos-media/services/openclaw/home`，而脚本原先直接把它当作 `.openclaw` 根使用，路径识别存在一层偏移

## 结构原则
- `/opt/fnos-media/services/openclaw`：服务运行根
- `/opt/fnos-media/services/edict-localized`：业务仓/安装仓/前台仓
- `/opt/fnos-media/services/edict-rebuild`：重建与派生产物仓

## 唯一真源
- 正式角色“太子”唯一真源：`taizi`
- `main` 只保留为 OpenClaw 运行时默认主入口，不再占用“太子”语义

## 本次修复
### 1. sync_agent_config.py
- `taizi` 继续映射为：`太子`
- `main` 改映射为：`主控 / 默认主入口`
- `main.workspace` 优先取 OpenClaw 默认 workspace，而不是误导性地落到角色 workspace 语义

### 2. utils.py
增强 `get_openclaw_home()`：
- 允许 `OPENCLAW_HOME` 直接指向 `.openclaw`
- 也兼容 `OPENCLAW_HOME` 指向其上一层 `home/`，并自动解析到 `home/.openclaw`

## 验证结果
修复后：
- `agent_config.json` 中不再有重复 `label=太子`
- `main` → `主控`
- `taizi` → `太子`

## 后续建议
如需进一步彻底收口，可在确认无兼容依赖后：
- 从 `openclaw.json` 的 `agents.list` 中移除显式 `main` 展示配置
- 将 `workspace-main` 明确标记为 legacy/canonical-data 兼容层

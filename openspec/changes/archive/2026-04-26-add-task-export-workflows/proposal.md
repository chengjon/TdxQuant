## Why

当前 task 层已经有稳定的场景入口，但输出仍以终端 JSON 和 `--output` 的整包结果为主。对于日常批量工作，还缺少“直接落文件”的稳定任务：

- 对一组固定关注标的，直接导出总览结果
- 对一个板块，直接导出研究结果

这类导出流程本质上是 task 层职责，而不是继续让调用方在 shell 外拼接二次处理脚本。

## What Changes

- 为 `TdxTaskManager` 新增 `watchlist_export`
- 为 `TdxTaskManager` 新增 `sector_research_export`
- 为 `task` CLI 新增 `watchlist-export`
- 为 `task` CLI 新增 `sector-research-export`
- 为 `runtime/task-profiles.json` 增加导出类 profile 和默认导出目录
- 为 task 层增加 JSON / CSV 文件落地能力
- 更新 task 层使用文档

## Capabilities

### Modified Capabilities

- `tdx-task-management`

### New Capability Surface

- `watchlist-export`
- `sector-research-export`

## Impact

- 让 task 层从“可编排”进一步变成“可直接落地使用”
- 不改变现有 `api` 原子入口和旧扁平命令兼容性
- 不涉及桌面自动化交易 capability

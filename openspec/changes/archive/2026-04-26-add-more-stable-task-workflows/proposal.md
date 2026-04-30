## Why

当前 task 层已经有基础骨架，但首批稳定任务仍然偏少，离“日常直接使用”还差一步。现有任务主要覆盖：

- 板块研究
- 公式扫描
- 环境刷新

日常使用里还缺两个高频稳定场景：

- 直接对一组关注标的做批量总览
- 以板块为起点，串联“板块成分提取 + 公式扫描”

这两个场景都属于典型 task 层职责：复用现有 manager 原子能力，减少手写命令拼接，且不引入桌面交易风险。

## What Changes

- 为 `TdxTaskManager` 新增 `watchlist_overview`
- 为 `TdxTaskManager` 新增 `sector_formula_scan`
- 为 `task` CLI 新增 `watchlist-overview`
- 为 `task` CLI 新增 `sector-formula-scan`
- 为 `runtime/task-profiles.json` 增加相应 profile
- 更新 task 层使用文档

## Capabilities

### Modified Capabilities

- `tdx-task-management`

### New Capability Surface

- `watchlist-overview`
- `sector-formula-scan`

## Impact

- 扩展 task 层的可用性，使其更接近日常批量使用
- 不改变现有 `api` 原子入口和旧扁平命令兼容性
- 不涉及桌面自动化交易 capability

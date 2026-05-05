## Context

当前 `block` 读侧已经有两条稳定主线：

- provider-level canonical read：
  - `block.read_watchlist_snapshot(...)`
- task-level daily entries：
  - `task block-read-watchlist`
  - `task block-read-watchlist-export`

`task block-read-full` 的作用不是定义新的 provider contract，而是在**同一 canonical snapshot** 之上增加一个更适合人工排查 / 运维诊断的 task-level 摘要视图。

## Goals / Non-Goals

**Goals**

- 把 `task block-read-full` 正式定义为稳定 task workflow。
- 明确 task 层只调用一次 `manager.block.read_watchlist_snapshot(...)`。
- 明确 task 成功结果保留 canonical `data.snapshot`，并额外补 `data.read_full`。
- 明确 task 失败结果透传底层 failure contract，不伪造 `data.read_full`。

**Non-Goals**

- 不新增 block read provider capability。
- 不增加第二次 raw read。
- 不增加 raw rows 返回。
- 不增加文件导出、preset、catalog、report 或写回逻辑。

## Decisions

### 1. `task block-read-full` 是高层 diagnostics task，不是第二套读取协议

`task block-read-full` 只是在成功 snapshot 之上整理一个 task-level diagnostics summary：

- `sector_name`
- `raw_member_count`
- `duplicate_count`
- `warnings_present`

调用方如果需要 canonical fields，仍然读取 `data.snapshot`。

### 2. Task 输入只接受 `block_code`

第一版只支持：

- `block_code`

不支持：

- 多 block
- 文件导入
- 导出参数
- 写入参数

### 3. 失败时不生成 `data.read_full`

如果 `manager.block.read_watchlist_snapshot(...)` 本身失败：

- 透传底层 `success/code/message/data/warnings/next_action`
- task 层只追加标准 task metadata
- 不生成 `data.read_full`

这样不会出现“失败结果但带着半套 success diagnostics”的歧义。

### 4. 继续沿用标准 task metadata 附着模式

`TdxTaskManager.block_read_full(...)` 继续使用：

- `_capture_task_timing(...)`
- `_attach_task_metadata(...)`

因此成功或失败结果都继续保留：

- `data.task`
- `data.task_profile`
- `data.timing`

## Risks / Trade-offs

- [把 task diagnostics summary 误写成新的 provider schema] → 通过要求 `data.snapshot` 继续作为 canonical contract 来规避。
- [scope 膨胀到导出 / preset / catalog] → 明确这些都不在本 change 中。
- [误导调用方以为 `block-read-full` 会返回 raw rows] → 明确 `data.read_full` 只是一组 diagnostics summary 字段。

## Migration Plan

1. 将 `task block-read-full` 作为独立 change 正式纳入 OpenSpec lifecycle。
2. 在 `tdx-task-management` 主 spec 中增加稳定 workflow requirement。
3. 保持现有实现与 focused tests 不变，仅同步 lifecycle 与主 spec。
4. 归档 change。

## Open Questions

- 无。第一版范围已经固定为独立高层 diagnostics task。

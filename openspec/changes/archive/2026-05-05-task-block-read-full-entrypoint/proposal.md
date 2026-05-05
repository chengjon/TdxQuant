## Why

`block.read_watchlist_snapshot` 的 provider-level canonical read 已经稳定，`task block-read-full` 的实现也已经进入工作树并通过 focused 回归，但这条高层读侧 diagnostics task 还没有正式 OpenSpec lifecycle。当前缺口不是继续扩功能，而是把“保留 canonical `data.snapshot`、只追加 task-level `data.read_full` 摘要、不引入第二次读取或专用导出逻辑”写进正式 change 和主 spec。

## What Changes

- 新增 `task-block-read-full-entrypoint` change，正式定义 `task block-read-full` 作为 `block.read_watchlist_snapshot` 之上的稳定高层 diagnostics task 入口。
- 固定 `TdxTaskManager.block_read_full(...)` 与 `task block-read-full` 的语义：
  - 输入只接受 `block_code`
  - 底层只调用一次 `manager.block.read_watchlist_snapshot(...)`
  - 成功时保留 provider-level `data.snapshot`，并追加 task-level `data.read_full`
  - 失败时透传底层 failure contract，不伪造 `data.read_full`
- 明确这条线不做：
  - 多 block 批量读取
  - raw rows 返回
  - 文件导出
  - task preset / catalog
  - 写回上层系统

## Capabilities

### Modified Capabilities
- `tdx-task-management`: 增加 `block-read-full` 稳定 task workflow，覆盖 task manager 与 task CLI 两个入口。

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
- Affected APIs:
  - `TdxTaskManager.block_read_full(...)`
  - `tdxquant task block-read-full ...`
- No new provider capability, export format, preset, catalog layer, or write-back workflow is introduced in this change.

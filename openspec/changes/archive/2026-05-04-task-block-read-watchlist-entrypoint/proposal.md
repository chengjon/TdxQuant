## Why

provider-level `block.read_watchlist_snapshot` 已经稳定落地，`task block-read-watchlist` 的实现也已经进入 `main`，但这条 task 场景入口还没有正式 OpenSpec lifecycle。当前缺口不是代码，而是把“薄 task 包装、沿用底层 snapshot contract、不重定义 task-only schema”写进正式 change 和主 spec。

## What Changes

- 新增 `task-block-read-watchlist-entrypoint` change，正式定义 `task block-read-watchlist` 作为 `block.read_watchlist_snapshot` 的稳定 task 场景入口。
- 固定 `TdxTaskManager.block_read_watchlist(...)` 与 `task block-read-watchlist` 的薄包装语义：
  - 输入只接受 `block_code`
  - 返回沿用底层 provider-level `data.snapshot`，同时附加标准 task metadata、task profile metadata 和 timing metadata
- 明确这条线不做：
  - 文件导出
  - task preset
  - catalog entry / bundle
  - task-only run artifact 或第二套 block-read snapshot schema

## Capabilities

### Modified Capabilities
- `tdx-task-management`: 增加 `block-read-watchlist` 稳定 task workflow，覆盖 task manager 与 task CLI 两个入口。

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
- Affected APIs:
  - `TdxTaskManager.block_read_watchlist(...)`
  - `tdxquant task block-read-watchlist ...`
- No new provider capability, export format, preset, or catalog layer is introduced in this change.

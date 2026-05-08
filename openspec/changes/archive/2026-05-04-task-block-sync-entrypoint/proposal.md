## Why

provider-level `block.sync_watchlist` 已经稳定，并且 `task block-sync` 的实现也已经落地到 `main`，但这条 task 场景入口还没有正式 OpenSpec lifecycle。当前缺口不是代码，而是把“薄 task 包装、沿用底层 sync contract、不重定义 task-only schema”写进正式 change 和主 spec。

## What Changes

- 新增 `task-block-sync-entrypoint` change，正式定义 `task block-sync` 作为 `block.sync_watchlist` 的稳定 task 场景入口。
- 固定 `TdxTaskManager.block_sync(...)` 与 `task block-sync` 的薄包装语义：
  - 输入参数映射到底层 `symbols + block_code + mode + create_if_missing + dry_run + mutation_key + show`
  - 返回沿用底层 provider-level block sync summary，同时附加 task metadata 与 timing metadata
- 明确这条线不做：
  - 文件导入
  - task preset
  - catalog entry / bundle
  - task-only run artifact 或第二套 block sync result schema

## Capabilities

### Modified Capabilities
- `tdx-task-management`: 增加 `block-sync` 稳定 task workflow，覆盖 task manager 与 task CLI 两个入口。

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
- Affected APIs:
  - `TdxTaskManager.block_sync(...)`
  - `tdxquant task block-sync ...`
- No new provider capability, transport, preset, or catalog layer is introduced in this change.

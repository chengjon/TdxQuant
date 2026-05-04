## Why

provider-level `block.read_watchlist_snapshot` 已经稳定，`task block-read-watchlist` 也已落地，但“读取后安全导出单文件 JSON”这条日常入口仍然只存在于代码实现里，没有正式 OpenSpec lifecycle。当前缺口不是再扩新 capability，而是把“task 层薄包装、保留底层 snapshot contract、只追加导出元数据”的语义正式写回 change 与主 spec。

## What Changes

- 新增 `task-block-read-watchlist-export-entrypoint` change，正式定义 `task block-read-watchlist-export` 作为 `block.read_watchlist_snapshot` 的稳定导出型 task 场景入口。
- 固定 `TdxTaskManager.block_read_watchlist_export(...)` 与 `task block-read-watchlist-export` 的薄包装语义：
  - 输入接受 `block_code`、显式 `output`、可选 `overwrite`
  - 先读取底层 provider-level `data.snapshot`
  - 成功时把 `data.snapshot` 以单文件 JSON 原子写到 `--output`
  - 返回保留底层 `data.snapshot`，同时附加 `data.export` 与标准 task metadata
- 明确这条线不做：
  - 新 provider capability
  - CSV / JSONL / Excel 导出
  - flat CLI
  - preset / catalog / report
  - task-only replay fixture

## Capabilities

### Modified Capabilities
- `tdx-task-management`: 增加 `block-read-watchlist-export` 稳定 task workflow，覆盖 task manager 与 task CLI 两个入口。

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
- Affected APIs:
  - `TdxTaskManager.block_read_watchlist_export(...)`
  - `tdxquant task block-read-watchlist-export ...`
- No new provider capability, transport, export format family, or catalog layer is introduced in this change.

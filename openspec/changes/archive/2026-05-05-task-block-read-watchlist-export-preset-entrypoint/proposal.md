## Why

`task block-read-watchlist-export` 已经作为稳定 task workflow 落地，但“把这条命令接进现有 task preset 体系”还只存在于代码实现里，没有正式 OpenSpec lifecycle。当前缺口不是再扩 preset schema，而是把“静态 `block_code / export_output / overwrite` 默认值、`task run --preset ...` 调度、显式 CLI 覆盖”的语义正式写回 change 与主 spec。

## What Changes

- 新增 `task-block-read-watchlist-export-preset-entrypoint` change，正式定义 `block-read-watchlist-export` 作为受支持的 task preset target。
- 固定第一版 preset contract：
  - 继续复用现有 task preset schema
  - `options` 只支持静态 `block_code`、`export_output`、`overwrite`
  - `task run --preset ...` 解析 preset 默认值后，仍走既有 `manager.block_read_watchlist_export(...)` workflow
- 固定覆盖语义：
  - CLI 显式 `--block-code`、`--export-output`、`--overwrite/--no-overwrite` 优先于 preset 默认值
- 明确这条线不做：
  - preset schema 扩展
  - 模板变量 / 路径插值
  - catalog entry

## Capabilities

### Modified Capabilities
- `tdx-task-management`: 增加 `block-read-watchlist-export` 的稳定 preset entrypoint，覆盖 task preset registry 与 `task run --preset ...` 调度语义。

## Impact

- Affected code:
  - `tdxquant/tasking.py`
  - `runtime/task-presets.json`
  - `tdxquant/cli.py`
  - `tests/test_api_cli.py`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
- Affected APIs:
  - `tdxquant task run --preset ...`
- No preset schema change, provider contract change, export format expansion, or catalog integration is introduced in this change.

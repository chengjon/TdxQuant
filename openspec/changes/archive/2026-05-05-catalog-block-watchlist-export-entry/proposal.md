## Why

`block-read-watchlist-export` 的 provider、task 和 preset 都已经稳定，但 `catalog` 层对它的发现与触发还只存在于代码实现里，没有正式 OpenSpec lifecycle。当前缺口不是扩 catalog schema，而是把“新增一条 task-source entry，复用现有 `catalog list/run/plan`”的语义正式写回 change 与主 spec。

## What Changes

- 新增 `catalog-block-watchlist-export-entry` change，正式定义 command catalog 对 `export-zxg-watchlist` 的支持。
- 固定第一版 catalog contract：
  - 继续复用现有 `runtime/command-catalog.json` schema
  - 新增一条 task-source entry：
    - `source = "task"`
    - `preset = "export-zxg-watchlist"`
  - 继续复用现有：
    - `catalog list`
    - `catalog list --entry ...`
    - `catalog plan --entry ...`
    - `catalog run --entry ...`
- 明确这条线不做：
  - 新 schema
  - `catalog show`
  - inline 参数输入
  - preset 编辑

## Capabilities

### Modified Capabilities
- `tdx-command-catalog`: 增加 block watchlist export preset-backed catalog entry，覆盖发现、plan 和 run 三条现有 catalog 路径。

## Impact

- Affected code:
  - `runtime/command-catalog.json`
  - `tests/test_api_cli.py`
- Affected APIs:
  - `tdxquant catalog list`
  - `tdxquant catalog plan --entry export-zxg-watchlist`
  - `tdxquant catalog run --entry export-zxg-watchlist`
- No provider/task/preset schema expansion is introduced in this change.

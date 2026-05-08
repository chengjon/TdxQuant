## Why

`read-zxg-watchlist`、`read-zxg-full` 和 `export-zxg-watchlist` 三条 block 读侧 task-backed catalog entry 已经稳定，但日常操作仍需要手工串联“先看标准化快照、再看完整诊断、最后导出 watchlist JSON”。当前缺口不是扩展 provider 或 task schema，而是把这条三步日常路径正式收口为一条稳定 catalog bundle，并把参数边界写回 OpenSpec。

## What Changes

- 新增 `catalog-block-read-watchlist-review-and-export-bundle` change，正式定义 command catalog 对 `read-zxg-review-and-export` 的支持。
- 固定第一版 bundle contract：
  - 继续复用现有 `runtime/command-bundles.json` schema
  - 新增一条 bundle：
    - `name = "read-zxg-review-and-export"`
    - step 1 = `read-zxg-watchlist`
    - step 2 = `read-zxg-full`
    - step 3 = `export-zxg-watchlist`
  - 继续复用现有：
    - `catalog list --kind bundle`
    - `catalog list --bundle ...`
    - `catalog plan --bundle ...`
    - `catalog run --bundle ...`
  - 新增 bundle-level `--block-code` fanout：
    - `catalog plan/run --bundle read-zxg-review-and-export --block-code <value>` MUST apply the same override to all three steps
  - 明确 `export_output` and `overwrite` remain owned by the `export-zxg-watchlist` preset
- 明确这条线不做：
  - 新 schema
  - bundle 内联参数建模
  - bundle 顶层 `--export-output` / `--overwrite`
  - 每步独立参数覆盖
  - 新 provider capability 或 task result schema

## Capabilities

### Modified Capabilities
- `tdx-command-catalog`: 增加 block read review-and-export bundle，覆盖 bundle 发现、plan、run、bundle-level `--block-code` fanout、preset-owned export 参数边界和 fail-fast 行为。

## Impact

- Affected code:
  - `runtime/command-bundles.json`
  - `tests/test_api_cli.py`
  - `openspec/specs/tdx-command-catalog/spec.md`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
- Affected APIs:
  - `tdxquant catalog list --kind bundle`
  - `tdxquant catalog list --bundle read-zxg-review-and-export`
  - `tdxquant catalog plan --bundle read-zxg-review-and-export`
  - `tdxquant catalog run --bundle read-zxg-review-and-export`
- No catalog schema, provider capability, or task result schema expansion is introduced in this change.

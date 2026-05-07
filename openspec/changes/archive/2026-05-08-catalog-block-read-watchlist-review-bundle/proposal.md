## Why

`read-zxg-watchlist` 和 `read-zxg-full` 两条 block 读侧 catalog entry 已经稳定，但把它们串成“先看标准化快照，再看完整诊断”的纯读 review bundle 还没有正式的 OpenSpec lifecycle。当前缺口不是扩 schema，而是把现有 bundle schema、既有 `catalog list/plan/run` 行为，以及 bundle-level `--block-code` 双步 fanout 语义正式写回 change 与主 spec。

## What Changes

- 新增 `catalog-block-read-watchlist-review-bundle` change，正式定义 command catalog 对 `read-zxg-review` 的支持。
- 固定第一版 bundle contract：
  - 继续复用现有 `runtime/command-bundles.json` schema
  - 新增一条 bundle：
    - `name = "read-zxg-review"`
    - step 1 = `read-zxg-watchlist`
    - step 2 = `read-zxg-full`
  - 继续复用现有：
    - `catalog list --kind bundle`
    - `catalog list --bundle ...`
    - `catalog plan --bundle ...`
    - `catalog run --bundle ...`
  - 新增 bundle-level `--block-code` fanout：
    - `catalog plan/run --bundle read-zxg-review --block-code <value>` MUST apply the same override to both steps
- 明确这条线不做：
  - 新 schema
  - bundle 内联参数建模
  - report/export/write-back
  - 每步独立参数覆盖

## Capabilities

### Modified Capabilities
- `tdx-command-catalog`: 增加 block read watchlist review bundle，覆盖 bundle 发现、plan、run 和 bundle-level `--block-code` fanout。

## Impact

- Affected code:
  - `runtime/command-bundles.json`
  - `tdxquant/cli.py`
  - `tests/test_api_cli.py`
  - `openspec/specs/tdx-command-catalog/spec.md`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
- Affected APIs:
  - `tdxquant catalog list --kind bundle`
  - `tdxquant catalog list --bundle read-zxg-review`
  - `tdxquant catalog plan --bundle read-zxg-review`
  - `tdxquant catalog run --bundle read-zxg-review`
- No catalog schema, provider capability, or task result schema expansion is introduced in this change.

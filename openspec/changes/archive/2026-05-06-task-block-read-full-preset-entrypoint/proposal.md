## Why

`task block-read-full` 已经作为稳定高层 diagnostics task 落地，但“把这条命令接进现有 task preset 体系”还只存在于代码实现里，没有正式 OpenSpec lifecycle。当前缺口不是再扩 preset schema，而是把“静态 `block_code` 默认值、`task run --preset ...` 调度、显式 CLI `--block-code` 覆盖、缺少 `block_code` 的早失败”这些语义正式写回 change 与主 spec。

## What Changes

- 新增 `task-block-read-full-preset-entrypoint` change，正式定义 `block-read-full` 作为受支持的 task preset target。
- 固定第一版 preset contract：
  - 继续复用现有 task preset schema
  - `options` 只支持静态 `block_code`
  - `task run --preset ...` 解析 preset 默认值后，仍走既有 `manager.block_read_full(...)` workflow
- 固定覆盖语义：
  - CLI 显式 `--block-code` 优先于 preset 默认值
- 固定最小 hardening：
  - 如果 `block-read-full` preset 缺少 `block_code`，`task run --preset ...` 必须稳定失败
- 明确这条线不做：
  - preset schema 扩展
  - 模板变量 / 路径插值
  - catalog / report / export / write-back 打包

## Capabilities

### Modified Capabilities
- `tdx-task-management`: 增加 `block-read-full` 的稳定 preset entrypoint，覆盖 task preset registry 与 `task run --preset ...` 调度语义。

## Impact

- Affected code:
  - `tdxquant/tasking.py`
  - `tdxquant/cli.py`
  - `runtime/task-presets.json`
  - `tests/test_api_cli.py`
  - `runtime/TdxQuant_Task_Layer_Usage.md`
- Affected APIs:
  - `tdxquant task run --preset ...`
- No preset schema change, provider contract change, export/report integration, or catalog integration is introduced in this change.

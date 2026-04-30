## Why

`block` 写操作已经成为上层项目最看重的 TongDaXin 差异化能力之一，但当前 `create_sector / delete_sector / rename_sector / clear_sector / send_user_block` 仍然只有普通成功失败语义，没有稳定的 mutation summary、审计产物或调用方关联键。这会让上层系统难以把板块写入视为可治理能力，也会让失败排查、重复调用关联和运行台账都缺少统一边界。

## What Changes

- Introduce a provider-facing block mutation safety contract for custom-sector write actions.
- Add normalized `block_mutation` summaries and durable local audit artifacts to block write results on both success and failure.
- Preserve an optional caller-supplied `mutation_key` for correlation without introducing automatic compare-and-skip idempotency behavior in this package.
- Extend manager and CLI block write entrypoints to accept mutation safety options and emit the same structured mutation contract.

## Capabilities

### New Capabilities
- `tdx-provider-block-mutation-safety`: Stable mutation summary and audit artifact contract for TongDaXin custom-sector write actions.

### Modified Capabilities
- `tdx-api-management`: Block-domain write actions now return standardized mutation summaries, audit artifact metadata, and accept optional mutation safety inputs.
- `tdx-api-cli-entry`: Nested `api` and flat bridge block-write commands now accept mutation safety arguments and emit the standardized mutation contract.

## Impact

- Affected code:
  - new shared block mutation safety helper module
  - `tdxquant/api/bridge.py`
  - `tdxquant/api/block.py`
  - `tdxquant/api/manager.py`
  - `tdxquant/cli.py`
- Affected tests:
  - bridge tests for block mutation normalization and audit artifacts
  - manager tests for block mutation metadata and provider artifacts
  - CLI parser and dispatch tests for new mutation safety arguments
- Affected docs:
  - new provider block mutation safety contract document
  - roadmap and function map references
- Compatibility:
  - existing block write entrypoints remain available
  - JSON result shape for block write actions gains capability-specific mutation fields and artifact references

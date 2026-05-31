## Why

D-07/D-08 now have a controlled `pingan-live-manual-acceptance` recorder, but promotion readiness still needs to fail closed when a live/manual acceptance artifact is hand-written, provenance-less, or otherwise not produced by that recorder.

## What Changes

- Add readiness evidence provenance to recorder-generated `tdx.desktop_trade.pingan_live_manual_acceptance.v1` artifacts.
- Make live/manual acceptance coverage require verified recorder provenance before it can satisfy the live/manual acceptance gate.
- Surface the live/manual acceptance recorder provenance status in `pingan_promotion_readiness_rollup` and block implemented-status review when it is missing or unverified.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary while preserving `[部分实现]`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: recorder artifacts and promotion readiness rollup must validate live/manual acceptance recorder provenance.
- `tdx-function-tree-registry`: D-07/D-08 must register this provenance-rollup gate as partial evidence only.

## Impact

- Affected code: `tdxquant/api/task.py`.
- Affected tests: `tests/test_api_manager.py`, `tests/test_function_tree_registry.py`.
- Affected specs: `tdx-task-management`, `tdx-function-tree-registry`.
- No broker, desktop, order, report, catalog, or bundle execution behavior changes.

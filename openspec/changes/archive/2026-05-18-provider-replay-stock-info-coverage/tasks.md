# Tasks

## 1. Specification

- [x] Add OpenSpec deltas for stock-info replay fixture coverage, default replay resolution, manager dispatch, and CLI entrypoints.
- [x] Validate the change with `openspec validate provider-replay-stock-info-coverage --strict`.

## 2. Tests

- [x] Add failing fixture catalog/loader assertions for `market-stock-info-success`.
- [x] Add failing replay-provider assertions for default `market.stock_info` replay execution.
- [x] Add failing manager/CLI assertions proving stock-info replay uses the fixture-backed manager path instead of live bridge code.

## 3. Implementation

- [x] Add the built-in `market-stock-info-success` fixture and descriptor.
- [x] Add the `market.stock_info` default replay mapping.
- [x] Route manager stock-info through `_dispatch_sync_capability`.
- [x] Enable nested and flat stock-info replay CLI paths.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-07 evidence and boundary without marking the whole node implemented.
- [x] Run focused pytest, OpenSpec validation, `git diff --check`, and the `FUNCTION_TREE.md` validator.
- [x] Archive the OpenSpec change and rerun verification.

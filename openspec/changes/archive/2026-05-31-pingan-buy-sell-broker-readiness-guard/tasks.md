# Tasks

## 1. Specification

- [x] Create proposal, design, tasks, and delta specs.
- [x] Validate the OpenSpec change before implementation.

## 2. Red Tests

- [x] Add trade manager tests proving buy/sell reject before desktop execution when broker readiness is required and health fails.
- [x] Add task manager tests proving trade-buy/trade-sell forward `require_broker_readiness`.
- [x] Add CLI parser/dispatch tests for direct trade buy/sell and task trade-buy/trade-sell.
- [x] Add FUNCTION_TREE registry assertion for D-07 evidence and boundary.

## 3. Implementation

- [x] Add the optional broker readiness guard to PingAn buy/sell manager paths.
- [x] Forward the option through task manager and CLI/gateway entrypoints.
- [x] Update `FUNCTION_TREE.md` D-07 evidence and boundary without status promotion.

## 4. Verification

- [x] Run focused pytest for trade manager, API/task manager, CLI, and FUNCTION_TREE registry coverage.
- [x] Run `openspec validate --all --strict`.
- [x] Run `python scripts/validate_function_tree_registry.py`.
- [x] Run `git diff --check`.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.

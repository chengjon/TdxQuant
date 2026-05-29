# Tasks

## 1. Specification

- [x] Add proposal, design, spec deltas, and tasks for restart preflight view.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing controller restart preflight ready test.
- [x] Add failing controller restart preflight missing/invalid metadata tests.
- [x] Add failing HTTP restart preflight dispatch test.
- [x] Add failing registry helper and CLI parser/dispatch tests.

## 3. Implementation

- [x] Add `SubscriptionWatchBackgroundController.restart_preflight()`.
- [x] Add bridge HTTP restart preflight route and handler.
- [x] Add registry client restart preflight helper.
- [x] Add CLI `bridge watch-restart-preflight` parser and dispatch.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.

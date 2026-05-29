# Tasks

## 1. Specification

- [x] Add proposal, design, spec deltas, and tasks for explicit restart control.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing controller restart success test using persisted `start_request`.
- [x] Add failing controller restart missing-start-request test.
- [x] Add failing HTTP restart dispatch test.
- [x] Add failing registry helper and CLI parser/dispatch tests.

## 3. Implementation

- [x] Add `SubscriptionWatchBackgroundController.restart()`.
- [x] Add bridge HTTP restart route and handler.
- [x] Add registry client restart helper.
- [x] Add CLI `bridge watch-restart` parser and dispatch.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.

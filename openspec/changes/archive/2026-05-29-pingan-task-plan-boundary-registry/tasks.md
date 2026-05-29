# pingan task plan boundary registry tasks

## 1. Specification

- [x] Add OpenSpec proposal/design/spec/tasks for D-07 read-only catalog plan boundary registration.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused API CLI tests for `task-buy` and `task-confirm-current` catalog plan summary boundaries.
- [x] Add a focused FUNCTION_TREE registry test for D-07 plan boundary evidence and non-execution wording.
- [x] Run the focused registry test and confirm it fails because D-07 evidence is stale.

## 3. Registry Update

- [x] Update `FUNCTION_TREE.md` D-07 evidence to cite `task-buy` / `task-sell` / `task-confirm-current` non-executing plan boundary coverage.
- [x] Keep D-07 `[部分实现]` and preserve boundaries for direct trade entries, catalog run, readiness, safety, and desktop exception coverage.

## 4. Verification

- [x] Run focused API CLI and FUNCTION_TREE registry tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this D-07 slice.

# subscription long-run control implemented registry tasks

## 1. Specification

- [x] Add OpenSpec proposal/design/spec/tasks for B-16/E-09 implemented registry closeout.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Test

- [x] Add a focused `FUNCTION_TREE.md` registry test for B-16/E-09 implemented status, lifecycle evidence, and bounded wording.
- [x] Run the focused test and confirm it fails because the registry is still stale.

## 3. Registry Update

- [x] Update `FUNCTION_TREE.md` B-16 main row to `[已实现]` with current lifecycle control evidence and explicit boundaries.
- [x] Update `FUNCTION_TREE.md` E-09 main row to `[已实现]` with current long-run wrapper evidence and explicit boundaries.
- [x] Keep supplemental notes compatible with the promoted main rows.

## 4. Verification

- [x] Run focused registry/subscription/bridge/CLI tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this registry slice.

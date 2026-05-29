# Tasks

## 1. Specification

- [x] Add proposal, design, spec deltas, and tasks for watch-status diagnostics view.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing CLI parser assertion for `bridge watch-status --view diagnostics`.
- [x] Add failing HTTP diagnostics-view assertion.
- [x] Add failing CLI diagnostics-view assertion.
- [x] Confirm focused tests fail because diagnostics view is unsupported or missing diagnostics fields.

## 3. Implementation

- [x] Add diagnostics view support to HTTP watch-status.
- [x] Add diagnostics view support to CLI watch-status.
- [x] Add a shared diagnostics projection from existing summary rollups.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.

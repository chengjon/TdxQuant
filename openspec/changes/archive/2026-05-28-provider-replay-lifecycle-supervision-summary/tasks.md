# provider replay lifecycle supervision summary tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only provider-replay lifecycle supervision summary.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused provider replay detailed status assertions for `lifecycle.supervision_summary`.
- [x] Add CLI summary-view assertions for `summary_view.lifecycle.supervision_summary`.
- [x] Run focused tests and confirm the failure is the missing supervision summary.

## 3. Implementation

- [x] Add the current disabled `supervision_summary` object to provider replay lifecycle status.
- [x] Project the object into the CLI summary view without adding start/stop/supervision behavior.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.

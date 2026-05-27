# provider replay probe advisory summary tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only `runtime.probe_summary.advisory_summary` and explicit non-lifecycle boundaries.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused provider replay status assertions for `runtime.probe_summary.advisory_summary`.
- [x] Add CLI summary-view assertions that the copied `probe_summary` exposes the same advisory object.
- [x] Run focused tests and confirm the failure is the missing advisory object.

## 3. Implementation

- [x] Derive `advisory_summary` from existing normalized probe rollup values in `tdxquant/provider_transport_replay.py`.
- [x] Keep CLI behavior unchanged except for the copied summary payload gaining the new object.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming readiness or lifecycle management.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.

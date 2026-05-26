# Tasks: Provider Replay Primary Requested Probe

## 1. OpenSpec

- [x] 1.1 Add OpenSpec proposal, design, tasks, and provider replay delta for primary requested probe.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add provider replay probe summary assertions for `primary_requested_probe`.
- [x] 2.2 Add CLI summary assertion for `primary_requested_probe`.

## 3. Implementation

- [x] 3.1 Derive `runtime.probe_summary.primary_requested_probe` from the existing requested target list.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming probe coverage or lifecycle control.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.

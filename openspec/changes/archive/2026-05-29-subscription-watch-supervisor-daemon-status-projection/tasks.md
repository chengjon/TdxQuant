## 1. OpenSpec

- [x] Create proposal, design, spec deltas, and tasks for read-only supervisor daemon status projection.
- [x] Validate the change before implementation.

## 2. Red Tests

- [x] Add failing background controller status test for the supervisor daemon read model.
- [x] Add failing bridge summary projection test for compact supervisor daemon status.
- [x] Add failing bridge diagnostics projection test for compact supervisor daemon status.

## 3. Implementation

- [x] Add supervisor daemon status to background `status()` without lifecycle side effects.
- [x] Add compact supervisor daemon projection to HTTP summary view.
- [x] Add compact supervisor daemon projection to HTTP diagnostics view.

## 4. Registry And Closeout

- [x] Update `FUNCTION_TREE.md` B-16/E-09 with evidence and explicit boundaries.
- [x] Run focused pytest, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change and repeat verification.
- [x] Commit only the files in this slice.

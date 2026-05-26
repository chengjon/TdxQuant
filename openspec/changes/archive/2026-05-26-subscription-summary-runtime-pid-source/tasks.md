# Tasks: Subscription Summary Runtime PID Source

## 1. OpenSpec

- [x] 1.1 Add OpenSpec proposal, design, tasks, and subscription summary delta for runtime PID source.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add HTTP watch-status summary assertion for `runtime.pid_source`.
- [x] 2.2 Add CLI watch-status summary assertion for `runtime.pid_source`.

## 3. Implementation

- [x] 3.1 Derive `runtime.pid_source` in HTTP and CLI runtime summary helpers when `runtime.pid` is projected.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming PID liveness or lifecycle control.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.

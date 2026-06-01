## 1. Contract and Tests

- [x] 1.1 Validate OpenSpec artifacts before implementation.
- [x] 1.2 Add focused red tests for managed lifecycle file lock acquire, blocked, and release diagnostics.
- [x] 1.3 Add adapter regression tests showing provider replay and subscription watch lock behavior is preserved through the shared primitive.

## 2. Implementation

- [x] 2.1 Implement shared non-blocking file lock acquire/release primitives in `tdxquant.managed_lifecycle`.
- [x] 2.2 Refactor provider replay statefile locking to use the shared primitive without changing public behavior.
- [x] 2.3 Refactor subscription watch control/supervisor locking to use the shared primitive without changing public behavior.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16 evidence and boundary for shared file lock primitives.
- [x] 3.2 Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 3.3 Archive the OpenSpec change, repeat verification, and commit only this slice.

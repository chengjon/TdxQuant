## 1. Tests

- [x] 1.1 Add parser coverage for `provider-replay status --probe-all`.
- [x] 1.2 Add handler coverage showing `--probe-all` calls all existing probe helpers without serving.

## 2. CLI Implementation

- [x] 2.1 Add `--probe-all` to the provider-replay status parser.
- [x] 2.2 Wire `--probe-all` to the existing health/watch-status/watch-events/watch-stream probe paths.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.

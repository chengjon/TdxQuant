## 1. Runtime API

- [x] 1.1 Add one-shot runtime bridge wrappers for subscribe, unsubscribe, and subscribed-stock-list operations.
- [x] 1.2 Expose those wrappers through `RuntimeApi` with stable operation metadata.

## 2. CLI

- [x] 2.1 Add `api subscription-subscribe`, `api subscription-unsubscribe`, and `api subscription-list` parser and dispatcher coverage.
- [x] 2.2 Ensure replay mode is rejected with explicit capability metadata.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` from designed/pending to partially implemented with one-shot boundaries.
- [x] 3.2 Add focused tests for runtime wrappers, CLI parse/dispatch, and replay rejection.
- [x] 3.3 Run focused tests, OpenSpec strict validation, `git diff --check`, and the `FUNCTION_TREE.md` registry validator.

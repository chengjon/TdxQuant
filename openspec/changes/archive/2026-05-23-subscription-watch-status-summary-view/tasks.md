## 1. Tests

- [x] 1.1 Add parser coverage for `bridge watch-status --view summary`.
- [x] 1.2 Add handler coverage that summary view prints `governance.action_summary`.
- [x] 1.3 Add regression coverage that detailed view remains the default.

## 2. CLI

- [x] 2.1 Add `--view detailed|summary` to `bridge watch-status`.
- [x] 2.2 Add a CLI-only summary payload builder for watch status responses.
- [x] 2.3 Keep bridge registry/HTTP request behavior unchanged.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automated governance.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.

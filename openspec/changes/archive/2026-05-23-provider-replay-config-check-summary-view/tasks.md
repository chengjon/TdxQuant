## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and provider replay service delta for the config-check summary view.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add parser coverage for `provider-replay config-check --view summary`.
- [x] 2.2 Add dispatch coverage proving summary view is config-only, non-serving, non-probing, and token-safe.

## 3. Implementation

- [x] 3.1 Add the config-check `--view` parser option with a detailed default.
- [x] 3.2 Attach an opt-in config-check `summary_view` without changing the existing detailed config payload.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary text.
- [x] 4.2 Run focused tests, OpenSpec validation, function-tree validation, and whitespace checks.
- [x] 4.3 Archive the OpenSpec change and re-run verification before committing.

## 1. Tests

- [x] 1.1 Add red coverage that `catalog plan --bundle sell-submit-once-pingan-complete-review --side buy --view summary` keeps the first step side as `sell`.
- [x] 1.2 Add regression coverage that entry-level `catalog plan --entry submit-once --side sell --view summary` still reports side `sell`.

## 2. Implementation

- [x] 2.1 Prevent top-level side override from leaking into bundle step namespace resolution.
- [x] 2.2 Preserve explicit step/preset side ownership for bundle steps.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-08 boundary for entry-scoped side override behavior.
- [x] 3.2 Run focused pytest, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.

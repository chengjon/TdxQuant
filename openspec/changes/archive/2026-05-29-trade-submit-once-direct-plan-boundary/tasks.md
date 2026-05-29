## 1. Tests

- [x] 1.1 Add red coverage that `catalog list --kind entry --label submit-once --view summary` discovers the direct trade `submit-once` entry.
- [x] 1.2 Add red coverage that `catalog plan --entry submit-once --view summary` exposes a non-executing direct submit-once trade boundary.
- [x] 1.3 Add red coverage that missing direct submit-once order inputs remain explicit while default `side=buy` is provided by the preset.

## 2. Implementation

- [x] 2.1 Add explicit `submit-once` catalog label and direct preset side default.
- [x] 2.2 Extend catalog plan/preview trade boundary metadata for direct `submit-once`.
- [x] 2.3 Preserve existing task buy/sell submit-once side-scoped planning.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-08 evidence and boundary without claiming workflow execution or production readiness.
- [x] 3.2 Run focused pytest, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.

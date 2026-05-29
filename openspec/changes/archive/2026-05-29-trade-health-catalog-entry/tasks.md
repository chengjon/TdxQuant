## 1. Tests

- [x] 1.1 Add red coverage that `catalog list --kind entry --label health --view summary` discovers `trade-health-pingan-readiness`.
- [x] 1.2 Add red coverage that `catalog plan --entry trade-health-pingan-readiness --view summary` exposes non-executing trade health boundary metadata and does not dispatch.

## 2. Implementation

- [x] 2.1 Add the health trade preset and command catalog entry.
- [x] 2.2 Register `health` as a supported trade preset command.
- [x] 2.3 Extend catalog plan/preview trade boundary metadata for health.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-07 evidence and boundary without claiming workflow execution or production readiness.
- [x] 3.2 Run focused pytest, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.

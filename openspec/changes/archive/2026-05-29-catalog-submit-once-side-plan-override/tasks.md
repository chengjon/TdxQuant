## 1. Tests

- [x] 1.1 Add red coverage that `catalog plan --entry submit-once --side sell --view summary` parses and reports side `sell` without dispatching.
- [x] 1.2 Add red coverage that `catalog preview --entry task-submit-once --side sell --view summary` reports side `sell` without dispatching.
- [x] 1.3 Add regression coverage that `catalog run --entry submit-once --side sell` remains unsupported by the parser.

## 2. Implementation

- [x] 2.1 Add plan/preview-only side parser support.
- [x] 2.2 Reuse existing catalog resolved namespace and trade boundary projection.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-08 evidence and boundary without claiming workflow execution or production readiness.
- [x] 3.2 Run focused pytest, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.

## 1. Specification

- [x] 1.1 Validate the OpenSpec change for trade audit requested-value diagnostics.

## 2. Test Coverage

- [x] 2.1 Add failing tests for daily and period `value_diagnostics` requested-value output.

## 3. Implementation

- [x] 3.1 Extract numeric price/quantity from audit result payloads and build requested-value diagnostics.
- [x] 3.2 Add `value_diagnostics` to daily and period trade audit report payloads.
- [x] 3.3 Update `FUNCTION_TREE.md` D-11 with explicit status, evidence, and boundary.

## 4. Verification

- [x] 4.1 Run focused API manager tests, OpenSpec validation, diff whitespace check, and the FUNCTION_TREE registry validator.
- [x] 4.2 Archive the OpenSpec change and re-run verification.

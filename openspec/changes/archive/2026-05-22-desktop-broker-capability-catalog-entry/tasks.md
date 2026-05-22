## 1. Specification

- [x] 1.1 Validate the OpenSpec change for the broker capability preset/catalog entry.

## 2. Test Coverage

- [x] 2.1 Add failing tests for `trade run --preset broker-capabilities-default` and `catalog plan --entry broker-capabilities`.

## 3. Implementation

- [x] 3.1 Add command-specific trade preset validation for the broker capability probe.
- [x] 3.2 Add the broker capability trade preset and command catalog entry.
- [x] 3.3 Update `FUNCTION_TREE.md` E-13 with explicit status, evidence, and boundary.

## 4. Verification

- [x] 4.1 Run focused CLI tests, OpenSpec validation, diff whitespace check, and the FUNCTION_TREE registry validator.
- [x] 4.2 Archive the OpenSpec change and re-run verification.

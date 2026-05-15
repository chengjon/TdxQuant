## 1. Probe Contract

- [x] 1.1 Add a focused extended broker capability probe builder for PingAn desktop with status, side-effect, evidence, and boundary fields.
- [x] 1.2 Add trade manager access to the probe without executing funds query, positions query, cancel order, or broker-native push subscription.

## 2. CLI And Risk Docs

- [x] 2.1 Add `trade broker-capabilities` parser and dispatcher coverage for the non-executing probe.
- [x] 2.2 Add an independent risk document for read-only, local-state-mutating, and broker-state-mutating extended broker capability boundaries.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` with an explicitly bounded partially implemented feature node.
- [x] 3.2 Add focused tests for the probe payload, CLI parser/dispatcher, unsupported broker rejection, and risk-document reference.
- [x] 3.3 Run focused tests, OpenSpec strict validation, `git diff --check`, and the `FUNCTION_TREE.md` registry validator.

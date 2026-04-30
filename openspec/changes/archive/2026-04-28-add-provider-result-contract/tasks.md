## 1. Contract Foundation

- [x] 1.1 Inventory current synchronous result shapes across manager-driven and CLI JSON-oriented query/formula paths.
- [x] 1.2 Introduce a shared synchronous provider result normalizer/helper for envelope fields, timing fields, runtime metadata, warnings, and artifacts.
- [x] 1.3 Define the initial stable field-format rules in code and docs for RFC3339 timestamps, string symbols, enum literals, and CLI error/result code handling.

## 2. Manager Integration

- [x] 2.1 Update manager-driven query/formula result wrapping to emit the provider-facing synchronous result envelope.
- [x] 2.2 Ensure manager-managed results include effective profile metadata, capability identity, capability version, schema version, and timing fields.
- [x] 2.3 Add or update manager tests that lock the new envelope for both success and failure paths.

## 3. CLI Integration

- [x] 3.1 Update nested `api` JSON-oriented outputs to serialize through the provider result contract.
- [x] 3.2 Update flat bridge JSON-oriented query/formula outputs to serialize through the same provider result contract.
- [x] 3.3 Enforce stable CLI exit-code semantics for JSON-oriented success/failure flows and add coverage for non-zero failure cases that still emit structured JSON.

## 4. Fixtures, Docs, and Validation

- [x] 4.1 Add minimal contract fixtures or golden examples for canonical synchronous success and failure envelopes.
- [x] 4.2 Document the breaking JSON-shape change and the intended provider-facing contract scope for upstream integrators.
- [x] 4.3 Run focused tests plus `openspec validate add-provider-result-contract --type change --strict` and capture any follow-up work needed for `formula.screen` and capability discovery changes.

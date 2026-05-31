## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn evidence provenance gate as partial evidence

`FUNCTION_TREE.md` SHALL register source evidence schema-contract validation as mainline D-07/D-08 evidence while keeping both nodes partial.

#### Scenario: D-07 and D-08 cite evidence contract without status promotion

- **GIVEN** PingAn promotion readiness rollup exposes `evidence_contract_status`
- **WHEN** D-07 and D-08 cite the provenance gate
- **THEN** both nodes SHALL remain `[部分实现]`
- **AND** both nodes SHALL cite `evidence_contract_status`
- **AND** both nodes SHALL cite `unverified_evidence_contract`
- **AND** both nodes SHALL cite `pingan-evidence-provenance-promotion-gate`
- **AND** both node boundaries SHALL say schema-contract validation is read-only
- **AND** both node boundaries SHALL say schema-contract validation does not prove production readiness or implemented status.

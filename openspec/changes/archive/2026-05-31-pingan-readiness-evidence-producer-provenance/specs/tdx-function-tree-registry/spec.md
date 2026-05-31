## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn readiness evidence producer provenance without status promotion

`FUNCTION_TREE.md` SHALL record that D-07/D-08 include producer-emitted artifact provenance for PingAn readiness evidence while keeping both nodes `[部分实现]`.

#### Scenario: Producer provenance is registered as partial implementation evidence

- **WHEN** `FUNCTION_TREE.md` describes D-07 and D-08
- **THEN** both rows SHALL mention `pingan-readiness-evidence-producer-provenance`
- **AND** both rows SHALL mention the producer provenance fields for preflight, dialog readiness, and acceptance coverage
- **AND** both rows SHALL keep status `[部分实现]`
- **AND** both rows SHALL state that producer provenance does not execute PingAn workflows, does not prove production readiness, and does not prove implemented status.


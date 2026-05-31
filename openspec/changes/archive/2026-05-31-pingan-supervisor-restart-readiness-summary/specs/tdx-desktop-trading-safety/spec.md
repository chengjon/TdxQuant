## ADDED Requirements

### Requirement: PingAn post-restart readiness summary SHALL remain evidence-only

PingAn post-restart readiness summary SHALL remain lifecycle evidence and MUST NOT imply order readiness, broker production readiness, UI login readiness, or live/manual acceptance.

#### Scenario: Recheck summary preserves readiness boundaries

- **WHEN** post-restart broker health recheck evidence is returned
- **THEN** it MUST include `order_submitted=false`
- **AND** it MUST state that `lifecycle_recovery_status=recovered` only means immediate broker health recheck returned OK
- **AND** it MUST not execute task/report/catalog workflows, submit orders, retry submissions, or promote D-07/D-08 implementation status.

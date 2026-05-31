## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn live manual acceptance evidence without promotion

`FUNCTION_TREE.md` SHALL register the live/manual acceptance evidence slice for D-07 and D-08 while preserving their `[部分实现]` status.

#### Scenario: D-07 and D-08 register live manual acceptance evidence

- **WHEN** trade audit reports can summarize optional live/manual acceptance evidence
- **THEN** D-07 and D-08 SHALL cite `pingan-live-manual-acceptance-evidence`
- **AND** D-07 and D-08 SHALL cite `live_manual_acceptance_complete`
- **AND** D-07 and D-08 SHALL cite `acceptance_complete`
- **AND** D-07 and D-08 SHALL remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents manual acceptance overclaiming

- **WHEN** D-07 or D-08 evidence cites live/manual acceptance report evidence
- **THEN** the boundary SHALL state that the evidence is read-only report evidence
- **AND** the boundary SHALL state that it does not execute trades or workflows
- **AND** the boundary SHALL state that it does not prove broker production readiness, UI login readiness, order safety, or implemented status.

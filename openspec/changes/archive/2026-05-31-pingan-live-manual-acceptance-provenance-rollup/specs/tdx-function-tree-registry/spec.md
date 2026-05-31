## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register live/manual acceptance provenance rollup without promotion

`FUNCTION_TREE.md` SHALL record that D-07 and D-08 include live/manual acceptance recorder provenance validation as partial promotion-readiness evidence only.

#### Scenario: D-07 and D-08 register live/manual recorder provenance while staying partial

- **WHEN** D-07 or D-08 cites `pingan-live-manual-acceptance-provenance-rollup`
- **THEN** the node status SHALL remain `[部分实现]`
- **AND** evidence SHALL mention `live_manual_acceptance_provenance_status`
- **AND** evidence SHALL mention `unverified_live_manual_acceptance_artifact_provenance`
- **AND** the boundary SHALL state that this is read-only recorder provenance validation and does not execute PingAn workflows, submit orders, prove production readiness, or promote implemented status.

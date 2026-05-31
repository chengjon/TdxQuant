## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn artifact provenance gate as partial evidence

`FUNCTION_TREE.md` SHALL register artifact provenance validation as mainline D-07/D-08 evidence while keeping both nodes partial.

#### Scenario: D-07 and D-08 cite artifact provenance gate without status promotion

- **GIVEN** PingAn promotion readiness rollup exposes `artifact_provenance_status`
- **WHEN** D-07 and D-08 cite the provenance gate
- **THEN** both nodes SHALL remain `[部分实现]`
- **AND** both nodes SHALL cite `artifact_provenance_status`
- **AND** both nodes SHALL cite `unverified_artifact_provenance`
- **AND** both nodes SHALL cite `pingan-artifact-provenance-promotion-gate`
- **AND** both node boundaries SHALL say artifact provenance validation is read-only
- **AND** both node boundaries SHALL say artifact provenance does not prove production readiness or implemented status.

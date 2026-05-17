## ADDED Requirements

### Requirement: Background watch status SHALL include status summary
The background subscription-watch control plane SHALL include a stable `status_summary` object in watch status responses.

#### Scenario: Caller receives bridge watch status
- **WHEN** a caller requests background watch status through the bridge control plane
- **THEN** the response MUST include raw `control`
- **AND** the response MUST include raw `watch_status`
- **AND** the response MUST include `status_summary`
- **AND** adding `status_summary` MUST NOT change watch start, stop, list, artifact, event, or log behavior

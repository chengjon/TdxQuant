## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include representative subscription-watch resilience artifacts
The system SHALL provide representative replay fixtures for subscription-watch reconnect and degraded runtime-state artifacts in addition to the existing completed-run samples.

#### Scenario: Fixture catalog includes reconnecting and degraded status samples
- **WHEN** a caller enumerates the built-in replay fixture catalog
- **THEN** the catalog MUST include representative `subscription-watch` status fixtures for `reconnecting` and `degraded`

#### Scenario: Fixture catalog includes a completed summary with reconnect history
- **WHEN** a caller enumerates the built-in replay fixture catalog
- **THEN** the catalog MUST include a representative completed `subscription-watch` summary that preserves reconnect history fields

#### Scenario: Existing completed fixtures remain valid with additive resilience fields
- **WHEN** a caller loads the existing completed `subscription-watch` status or summary fixture
- **THEN** the fixture MUST remain valid for the pre-existing completed-run contract
- **AND** any resilience fields added by this change MUST be additive compatibility extensions rather than a breaking schema rewrite

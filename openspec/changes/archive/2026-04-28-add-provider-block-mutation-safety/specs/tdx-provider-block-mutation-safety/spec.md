## ADDED Requirements

### Requirement: Provider block mutation safety SHALL expose a stable mutation summary
The system SHALL expose a stable capability-specific mutation summary for TongDaXin custom-sector write actions so callers can reason about attempted state changes without parsing free-form messages.

#### Scenario: Block write returns normalized mutation summary
- **WHEN** a caller invokes a provider-facing custom-sector write action
- **THEN** the response `data` MUST include a `block_mutation` object with stable identity, operation, target, and status fields

### Requirement: Provider block mutation safety SHALL write a durable local audit artifact for every write attempt
The system SHALL write a local JSON audit artifact for every supported custom-sector write attempt, including failed attempts.

#### Scenario: Successful block mutation writes audit artifact
- **WHEN** a custom-sector write action succeeds
- **THEN** the response MUST expose an audit artifact path and the written audit file MUST describe the attempted mutation and its result

#### Scenario: Failed block mutation also writes audit artifact
- **WHEN** a custom-sector write action fails
- **THEN** the response MUST still expose an audit artifact path and the written audit file MUST capture the failed attempt

### Requirement: Provider block mutation safety SHALL preserve an optional caller mutation key
The system SHALL preserve an optional caller-supplied `mutation_key` across the result payload and audit artifact without silently converting that key into automatic compare-and-skip behavior.

#### Scenario: Caller provides mutation key
- **WHEN** a caller passes a `mutation_key` for a supported custom-sector write action
- **THEN** the response `data.block_mutation` and audit artifact MUST contain the same key
- **AND** the action MUST still execute normally unless the underlying runtime itself rejects it

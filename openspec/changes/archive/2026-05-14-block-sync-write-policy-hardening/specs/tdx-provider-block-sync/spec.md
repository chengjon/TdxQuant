## ADDED Requirements

### Requirement: Provider block sync SHALL harden mutation-key replay and conflict feedback
The system SHALL make mutation-key replay and conflict outcomes explicit and machine-readable.

#### Scenario: Same mutation key and same canonical policy request replays prior result
- **WHEN** a caller repeats a block sync request with the same mutation key and same canonical request including policy metadata
- **THEN** block sync MUST return a replay outcome without live mutation writes
- **AND** the response MUST include mutation-key replay metadata

#### Scenario: Same mutation key and different canonical policy request returns conflict
- **WHEN** a caller repeats a block sync request with the same mutation key and a different canonical request including policy metadata
- **THEN** block sync MUST return a stable conflict outcome
- **AND** the response MUST include prior and current canonical request metadata

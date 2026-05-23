## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose compact replay source

The provider replay status summary view SHALL expose compact replay-source provenance derived from the detailed status payload without copying full fixture path detail or changing daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary source view

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the summary view MUST include `replay_source.source_kind`
- **AND** the summary view MUST include `replay_source.fixture`
- **AND** the summary view MUST include `replay_source.fixture_path_provided`
- **AND** the summary view MUST NOT include full `replay_source.fixture_path`
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service

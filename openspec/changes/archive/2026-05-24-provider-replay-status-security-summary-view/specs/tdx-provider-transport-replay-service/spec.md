## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose compact security boundary

The provider replay status summary view SHALL expose compact security boundary metadata derived from the detailed status payload without exposing bearer tokens, allowlist members, or changing daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary security view

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the summary view MUST include `security.bearer_token_required`
- **AND** the summary view MUST include `security.source_allowlist_enabled`
- **AND** the summary view MUST include `security.master_allowlist_count`
- **AND** the summary view MUST NOT include bearer token values
- **AND** the summary view MUST NOT include full allowlist members
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service

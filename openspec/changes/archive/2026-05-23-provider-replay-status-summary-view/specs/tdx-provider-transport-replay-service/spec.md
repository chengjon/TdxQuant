## ADDED Requirements

### Requirement: Provider replay status CLI SHALL expose an opt-in summary view

The provider replay status CLI SHALL expose an opt-in summary view that projects existing lifecycle and probe-rollup fields without changing the default detailed status output or daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary view

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the CLI MUST include `summary_view.mode=summary`
- **AND** the summary view MUST include lifecycle boundary fields, runtime observation flags, `probe_summary`, and boundaries
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service

#### Scenario: Caller omits provider replay status summary view

- **WHEN** a caller executes `provider-replay status --config <path>`
- **THEN** the CLI MUST preserve the existing detailed status payload
- **AND** it MUST NOT require callers to consume a summary projection

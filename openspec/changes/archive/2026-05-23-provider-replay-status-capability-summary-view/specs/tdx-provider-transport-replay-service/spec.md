## MODIFIED Requirements

### Requirement: Provider replay status CLI SHALL expose an opt-in summary view

The provider replay status CLI SHALL expose an opt-in summary view that projects existing lifecycle and probe-rollup fields without changing the default detailed status output or daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary view

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** the command MUST include `summary_view`
- **AND** the summary view MUST include lifecycle boundary fields, runtime observation flags, `probe_summary`, compact read-only capability fields, and boundaries
- **AND** the summary view MUST NOT replace the detailed `status` payload
- **AND** the command MUST NOT start, stop, restart, supervise, or schedule a replay service

#### Scenario: Caller omits provider replay status summary view

- **WHEN** a caller runs `provider-replay status --config <path>` without `--view summary`
- **THEN** the command MUST keep returning the detailed status payload without `summary_view`

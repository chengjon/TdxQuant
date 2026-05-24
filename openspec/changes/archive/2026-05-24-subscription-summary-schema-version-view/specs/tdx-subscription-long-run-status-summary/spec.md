## ADDED Requirements

### Requirement: Subscription summary views SHALL expose status summary schema version

The subscription long-run CLI and HTTP summary views SHALL include additive read-only `status_summary.schema_version` when the underlying detailed status summary provides it, without exposing raw `control`, raw `watch_status`, full governance reasons, full governance actions, or changing reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: CLI summary view includes status summary schema version

- **WHEN** a caller runs `bridge watch-status --view summary`
- **AND** the underlying detailed payload includes `status_summary.schema_version`
- **THEN** the CLI summary result MUST include the same `status_summary.schema_version`
- **AND** the summary result MUST continue to omit raw `control`, raw `watch_status`, full `governance.reasons`, and full `governance.actions`

#### Scenario: HTTP summary view includes status summary schema version

- **WHEN** a caller requests `watch/status?view=summary`
- **AND** the underlying detailed payload includes `status_summary.schema_version`
- **THEN** the HTTP summary result MUST include the same `status_summary.schema_version`
- **AND** the summary result MUST continue to omit raw `control`, raw `watch_status`, full `governance.reasons`, and full `governance.actions`

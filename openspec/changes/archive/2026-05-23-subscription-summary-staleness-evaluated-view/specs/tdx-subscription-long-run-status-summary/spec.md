## ADDED Requirements

### Requirement: Subscription summary view SHALL expose staleness evaluation flag

The subscription long-run HTTP and CLI summary views SHALL include the read-only `governance.staleness_evaluated` flag when the underlying status summary provides it, without exposing full governance actions or changing reconnect/backoff behavior.

#### Scenario: HTTP summary view includes staleness evaluation flag

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.staleness_evaluated`
- **THEN** the HTTP summary result MUST include `governance.staleness_evaluated`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`

#### Scenario: CLI summary view includes staleness evaluation flag

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.staleness_evaluated`
- **THEN** the CLI summary payload MUST include `governance.staleness_evaluated`
- **AND** the CLI summary payload MUST continue to omit full `governance.actions`

#### Scenario: Summary flag remains projection-only

- **WHEN** the summary view includes `governance.staleness_evaluated`
- **THEN** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

## ADDED Requirements

### Requirement: Subscription summary views SHALL expose advisory governance boundary

The subscription long-run HTTP and CLI summary views SHALL include the read-only `governance.boundary` marker when the underlying status summary provides it, without exposing full governance actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance boundary

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.boundary`
- **THEN** the HTTP summary result MUST include `governance.boundary`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance boundary

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.boundary`
- **THEN** the CLI summary result MUST include `governance.boundary`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

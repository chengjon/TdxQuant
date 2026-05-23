## ADDED Requirements

### Requirement: Subscription summary views SHALL expose governance reason count

The subscription long-run HTTP and CLI summary views SHALL include a read-only `governance.reason_count` derived from the underlying detailed `governance.reasons` list when that list is present, without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance reason count

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes a `governance.reasons` list
- **THEN** the HTTP summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance reason count

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes a `governance.reasons` list
- **THEN** the CLI summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

## ADDED Requirements

### Requirement: Subscription summary views SHALL expose governance sample counts

The subscription long-run HTTP and CLI summary views SHALL include read-only `governance.reason_sample_count` and `governance.action_sample_count` fields derived from their bounded visible sample arrays when those arrays are projected, without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance sample counts

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.reason_sample_count` equal to the length of `governance.reason_samples`
- **AND** the HTTP summary result MUST include `governance.action_sample_count` equal to the length of `governance.action_samples`
- **AND** the HTTP summary result MUST keep `governance.reason_count` and `governance.action_count` as full underlying list counts
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance sample counts

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the CLI summary result MUST include `governance.reason_sample_count` equal to the length of `governance.reason_samples`
- **AND** the CLI summary result MUST include `governance.action_sample_count` equal to the length of `governance.action_samples`
- **AND** the CLI summary result MUST keep `governance.reason_count` and `governance.action_count` as full underlying list counts
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

## ADDED Requirements

### Requirement: Subscription summary views SHALL expose governance hidden sample counts

The subscription long-run HTTP and CLI summary views SHALL include read-only `governance.reason_sample_hidden_count` and `governance.action_sample_hidden_count` fields derived from the difference between full underlying governance list counts and bounded visible sample counts when those samples are projected, without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance hidden sample counts

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.reason_sample_hidden_count` equal to `governance.reason_count - governance.reason_sample_count`
- **AND** the HTTP summary result MUST include `governance.action_sample_hidden_count` equal to `governance.action_count - governance.action_sample_count`
- **AND** the hidden counts MUST be non-negative integers
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes governance hidden sample counts

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the CLI summary result MUST include `governance.reason_sample_hidden_count` equal to `governance.reason_count - governance.reason_sample_count`
- **AND** the CLI summary result MUST include `governance.action_sample_hidden_count` equal to `governance.action_count - governance.action_sample_count`
- **AND** the hidden counts MUST be non-negative integers
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

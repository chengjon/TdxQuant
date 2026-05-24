## ADDED Requirements

### Requirement: Subscription summary views SHALL expose bounded governance reason samples

The subscription long-run HTTP and CLI summary views SHALL include bounded read-only `governance.reason_samples` derived from the underlying detailed `governance.reasons` list when that list is present, without exposing the full reasons/actions arrays or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes bounded governance reason samples

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes multiple `governance.reasons`
- **THEN** the HTTP summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the HTTP summary result MUST include `governance.reason_samples`
- **AND** the HTTP summary result MUST include `governance.reason_sample_limit`
- **AND** the HTTP summary result MUST include `governance.reason_sample_truncated`
- **AND** the HTTP summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

#### Scenario: CLI summary view includes bounded governance reason samples

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes multiple `governance.reasons`
- **THEN** the CLI summary result MUST include `governance.reason_count` equal to the length of that list
- **AND** the CLI summary result MUST include `governance.reason_samples`
- **AND** the CLI summary result MUST include `governance.reason_sample_limit`
- **AND** the CLI summary result MUST include `governance.reason_sample_truncated`
- **AND** the CLI summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the CLI summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes


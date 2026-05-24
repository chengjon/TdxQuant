## ADDED Requirements

### Requirement: Subscription summary views SHALL expose bounded governance action samples

The subscription long-run HTTP and CLI summary views SHALL include bounded read-only `governance.action_samples` derived from the underlying detailed `governance.actions` list when that list is present, without exposing the full action list or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes bounded governance action samples

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status summary includes multiple `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.action_samples`
- **AND** each action sample MUST include compact action metadata such as action, reason, and severity without the full description text
- **AND** the HTTP summary result MUST include `governance.action_sample_limit`
- **AND** the HTTP summary result MUST include `governance.action_sample_truncated`
- **AND** the HTTP summary result MUST NOT include full `governance.actions`
- **AND** the summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes

#### Scenario: CLI summary view includes bounded governance action samples

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes multiple `governance.actions`
- **THEN** the CLI summary result MUST include `governance.action_samples`
- **AND** each action sample MUST include compact action metadata such as action, reason, and severity without the full description text
- **AND** the CLI summary result MUST include `governance.action_sample_limit`
- **AND** the CLI summary result MUST include `governance.action_sample_truncated`
- **AND** the CLI summary result MUST NOT include full `governance.actions`
- **AND** the CLI summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes


## ADDED Requirements

### Requirement: Subscription summary view SHALL expose governance sample summary

Subscription long-run HTTP and CLI summary views SHALL include additive read-only `governance.sample_summary` metadata derived from the existing bounded reason/action sample projection without exposing full governance reasons/actions or changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes governance sample summary

- **WHEN** a caller requests the worker bridge watch-status HTTP summary view and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the HTTP summary result MUST include `governance.sample_summary.reason_count` equal to the full underlying reason count
- **AND** it MUST include `reason_sample_count`, `reason_sample_hidden_count`, `reason_sample_limit`, and `reason_sample_truncated` matching the sibling governance sample fields
- **AND** it MUST include `action_count`, `action_sample_count`, `action_sample_hidden_count`, `action_sample_limit`, and `action_sample_truncated` matching the sibling governance sample fields
- **AND** hidden counts MUST be non-negative integers
- **AND** the HTTP summary result MUST continue to omit full `governance.reasons`
- **AND** the HTTP summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged
#### Scenario: CLI summary view includes governance sample summary

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reasons` and `governance.actions`
- **THEN** the CLI summary result MUST include `governance.sample_summary.reason_count` equal to the full underlying reason count
- **AND** it MUST include `reason_sample_count`, `reason_sample_hidden_count`, `reason_sample_limit`, and `reason_sample_truncated` matching the sibling governance sample fields
- **AND** it MUST include `action_count`, `action_sample_count`, `action_sample_hidden_count`, `action_sample_limit`, and `action_sample_truncated` matching the sibling governance sample fields
- **AND** hidden counts MUST be non-negative integers
- **AND** the CLI summary result MUST continue to omit full `governance.reasons`
- **AND** the CLI summary result MUST continue to omit full `governance.actions`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

## MODIFIED Requirements

### Requirement: Bridge watch-status CLI SHALL expose summary view

The bridge watch-status CLI SHALL expose an opt-in summary view that projects the existing detailed watch status payload without changing bridge HTTP, worker, reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: Caller requests bridge watch-status summary view

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI MUST still call the existing bridge watch-status request path
- **AND** the CLI MUST print a compact JSON payload
- **AND** the compact payload MUST include selected runtime identity fields derived from `control` and `watch_status` when present
- **AND** the compact payload MUST include `status_summary.governance.action_summary` when the detailed payload provides it
- **AND** the detailed payload MUST remain the default when no summary view is requested

#### Scenario: Bridge watch-status summary view preserves advisory boundary

- **WHEN** the detailed watch status payload contains governance advisory output
- **THEN** the summary view MUST treat governance fields and runtime identity fields as read-only projection data
- **AND** the summary view MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes
